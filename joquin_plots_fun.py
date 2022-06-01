from shipcal import Weather, Consumer, Collector
from bokeh.plotting import show, figure

# This is just for the type hint you can ignore it.
from bokeh.plotting.figure import Figure


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
    # This "self" variable is where you get the data from, this line will
    # help for the trasition to a class method
    self = Weather("src/shipcal/weather/data/Sevilla.csv")

def get_energy_plot():
    pass


if __name__ == "__main__":
    show(get_dni_plot())
    show(get_iams_plot())
    show(get_energy_plot())
