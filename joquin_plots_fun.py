# This is just for the type hint you can ignore it.
from bokeh.plotting.figure import Figure
import pandas as pd
import numpy as np

from shipcal import Weather, Collector  # , Consumer
from bokeh.plotting import show, figure


def get_weather_plot(property_name: str = "dni") -> Figure:
    """
    Uses the atributes of an instance of a Weather class to create a
    bokeh figure of the desired weather property against the timeindex.

    Parameters
    ----------
    property_name : str, optional
        Weather's property name, by default "dni"

    Returns
    -------
    Figure
        bokeh figure for later plotting or html embed
    """

    # This "self" variable is where you get the data from, this line will
    # help for the trasition to a class method
    self = Weather("src/shipcal/weather/data/Sevilla.csv")

    # Code from here, the next lines may be useful but feel free to do
    # it differently

    self.__getattribute__(property_name)

    graph = figure()

    return graph


def get_iams_plot():
    """
    Returns a plot of three lines for each kinf of IAM; transeversal,
    longitudinal and global vs incidence angle.

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
    angles_df = pd.DataFrame({
        "incidence_angle": np.linspace(0, 180, 180),
        "iam_long": np.linspace(0, 180, 180),
        "iam_tran": np.linspace(0, 180, 180),
        "iam": np.linspace(0, 180, 180)
    })
    iams_df = pd.DataFrame(
        angles_df["incidence_angle"].apply(self.get_iam).to_list(),
        columns=["iam_long", "iam_tran", "iam"]
    )

    # This dataframe contains 4 cols, [angle, iam_long, iam_tran, iam]
    iams_df = pd.concat([iams_df, angles_df], axis=1)

    graph = figure()

    return graph


def get_energy_plot():
    pass


if __name__ == "__main__":
    show(get_weather_plot())
    show(get_weather_plot("amb_temp"))
    show(get_iams_plot())
    # show(get_energy_plot())
