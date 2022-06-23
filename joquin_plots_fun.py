from datetime import datetime, timedelta
from typing import List

# This is just for the type hint you can ignore it.
from bokeh.plotting.figure import Figure

import pandas as pd
import numpy as np

from shipcal import Weather, Collector  # , Consumer
from bokeh.plotting import show, figure


def get_weather_plot(time_range: List[datetime] = None, property_name: List[str] = None) -> Figure:
    """
    Uses the atributes of an instance of a Weather class to create a
    bokeh figure of the desired weather property against the timeindex.

    Parameters
    ----------
    time_range : List[datetime]
        List of two datetimes to select the time range in which the poperty
        is to be selected.
    property_name : List[str], optional
        Weather's property names, by default None

    Returns
    -------
    Figure
        bokeh figure for later plotting or html embed
    """

    # This "self" variable is where you get the data from, this line will
    # help for the trasition to a class method
    self = Weather("src/shipcal/weather/data/Sevilla.csv")

    if property_name is None:
        property_name = "dni"

    # Code from here, the next lines may be useful but feel free to do
    # it differently

    begin_day=time_range[0].timetuple().tm_yday-1 # Calculates the day of the year to start and to end the plot
    end_day=time_range[1].timetuple().tm_yday-1   # the day count starts from 0
    
    begin_hour=begin_day*24 # Calculates the hour of the year 
    end_hour=end_day*24     # to star and to end the plot

    weather_variable=self.__getattribute__(property_name) #Saves the climate property to plot into a variable 
    
    y=weather_variable[begin_hour:end_hour] #Creates a padas series with the desired hours
    
    x = np.array([time_range[0] + timedelta(hours=i) for i in range(end_hour-begin_hour)]) # Creates an array with the timedates 
                                                                                           # from the start till the end of the plot
    
    TOOLTIPS = [(f'({weather_variable.name})', "($y)")]
    graph = figure(title=weather_variable.name, x_axis_label="Date",x_axis_type='datetime', # Creates the base figure
                   tools='pan,box_zoom,reset,tap,wheel_zoom,save,hover',tooltips=TOOLTIPS)  # 
    

    graph.line(x,y,line_width=2) #Creates the line plot 
    
    return graph



def get_iams_plot(time_range: List[datetime] = None):
    """
    Returns a plot of three lines for each kinf of IAM; transeversal,
    longitudinal and global vs incidence angle.

    Parameters
    ----------
    time_range : List[datetime]
        List of two datetimes to select the time range in which the poperty
        is to be selected.

    Returns
    -------
    Figure
        bokeh figure for later plotting or html embed
    """
    # This "self" variable is where you get the data from, this line will
    # help for the trasition to a class method
    self = Collector(
        eff_opt_norm=0.68, nu_1=0.043, nu_2=0.0010, mdot_test=0.5,
        aperture_area=13,
        iam_file="src/shipcal/collectors/data/SOLATOM_real.csv",
        azimuth_field=0, roll_field=0, pitch_field=0
    )

    # Start coding here, the next lines may be useful but feel free to do
    # it differently
    iams_list=[] #Creates an empty list to save the iams values
    
    incidence_angle=np.arange(0,91)   #Creates an array from 0 to 90 
    
    iams_list.append([self.get_iam(theta_long=i,theta_trans=i) for i in incidence_angle]) #Calculates the transversal, 
                                                                                          #longitudinal and global iam 
                                                                                          #and saves them into the list
            
    iams_array=np.array(iams_list) #Transform the iams_list into an array
    
    iams_array=iams_array.reshape((int(iams_array.size/3),3)) #Reshape to a 90,3 array 
    
    iams_df=pd.DataFrame(iams_array,columns=["iam_long", "iam_tran", "iam"]) #Creates a pandas dataframe with the three iams
    iams_df['incidence_angle']=incidence_angle #Add a column to the dataframe with the incidence angle
    
    y1=iams_df['iam_long']       #Variable for plotting the longitudial iam 
    y2=iams_df['iam_tran']       #Variable for plotting the transversal iam
    y3=iams_df['iam']            #Variable for plotting the global iam
    x=iams_df['incidence_angle'] #Variable with the x axis
    
    TOOLTIPS = [("(Angle, IAMs)", "($x, $y)")] #Variable for the plot inspector

    graph = figure(title='IAM vs Incidence angle',plot_width=700, plot_height=500,     # Creates the base figure
                   tools='pan,box_zoom,hover,reset,wheel_zoom,save',tooltips=TOOLTIPS) #
    
    graph.line(x, y1, legend_label="Longitudinal.", color="blue", line_width=2) # Plot line for the longitudinal iam
    graph.line(x, y2, legend_label="Trasversal", color="red", line_width=2)     # Plot line for the transversal iam
    graph.line(x, y3, legend_label="Global", color="green", line_width=2)       # Plot line for the global iam

    return graph


def get_energy_plot():
    pass


if __name__ == "__main__":
    show(get_weather_plot())
    show(get_weather_plot("amb_temp"))
    show(get_iams_plot())
    # show(get_energy_plot())
