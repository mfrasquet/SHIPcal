
from logging import exception
from src.shipcal import Weather  # , Collector, Consumer


def _is_coherent_weather() -> None:
    """
    This method will test if the instance of the Weather class is
    coherent with in the DNI and solar position. Available DNI when
    the sun is under the horizon is not acceptable.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    """
    
    self = Weather("src/shipcal/weather/data/Sevilla_Error.csv", step_resolution="10min")
    self.dni  # This is a pd.Series with the dni
    self.solar_elevation  # [°] Sun elevation from the astronomical horizon.

    
    filter_dni= self.dni>100  # Checks if DNI is greather than a certain threshold.
    filter_elev = self.solar_elevation<=0  # Checks if the sun is bellow the astronomical horizon.
    filter_both = filter_dni & filter_elev  # Check if both conditions are met.
    
    
    if filter_both.any():  # If any value of the filter is True, means that the TMY has an error. Else, do nothing.
        
        dni_error = self.dni[filter_both]  # Pandas Series containing TMYs corrupted rows (Based on DNI).
        
        # Raise Exception, indicating first and last corrupted rows, based on their index (datetime).
        raise Exception(
            "Incoherent Weather. There is non-zero DNI when sun is"
            f" under the horizon between the times {str(dni_error.index[0])}" 
            f" and {str(dni_error.index[-1])}"
            )



if __name__ == "__main__":
    _is_coherent_weather()
