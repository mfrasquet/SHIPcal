"""
This module contains the test for the Weather class
"""
import pytest

from shipcal import Weather
from datetime import datetime

def test_read_tmy3():
    """ Check that tmy3 format is bein read correctly """
    sevilla_tmy3_loc = "src/shipcal/weather/data/Sevilla.csv"
    sevilla = Weather(sevilla_tmy3_loc)
    assert sevilla.lat == 37.410

def test_localtime_to_solartime():
    """
    Test if a few of the data index changed properly to solar time
    assuming that were localtime
    """
    sevilla_tmy3_loc = "src/shipcal/weather/data/Sevilla.csv"
    # Should receive a parameter that states that the data is local time
    # to be converted
    sevilla = Weather(sevilla_tmy3_loc, local_time=True)
    # This is the same tmy without convertion. Just to compare
    sevilla_localtime = Weather(sevilla_tmy3_loc)

    # Consider at a location at the east of the greenwich tz
    # Then, for sevilla, the 12:00 h of the 01/01/2005 must be 10:33
    assert sevilla_localtime.dni.loc["2005-01-01 12:00:00+0100"] == sevilla.dni[11]
    assert sevilla.dni.index[11].time() == datetime.time(datetime(day=1,month=1,year=2022,hour=10, minute=33))

    # Consider daytime saving
    # Then, for sevilla, the 12:00 h of the 30/03/2005 must be 09:31
    assert sevilla_localtime.dni.loc["2005-03-30 12:00:00+0100"] == sevilla.dni[2123]
    assert sevilla.dni.index[2123].time() == datetime.time(datetime(day=1,month=1,year=2022,hour=9, minute=31))

    # Consider a  location at the east of the greenwich tz

def test_sunposition():
    """
    Tests that the sun position is correct for few dates and locations
    """
    sevilla_tmy3_loc = "src/shipcal/weather/data/Madrid_false.csv"
    sevilla = Weather(sevilla_tmy3_loc)
    
    # The altitude in the step 13 (the 14 h) in Sevilla must be
    # This takes the datetime in the 16th element in the data
    sevilla.get_solar_altitude(13) == pytest.approx(59.75,0.05)
    # and azimut
    sevilla.get_solar_azimut(13) == pytest.approx(65.67,0.05)

    # I should be able to find the same altitude by entering a datetime
    # This should return the solar altitude in
    # the datetime '2005-01-01 17:00:00+0100'
    sevilla.get_solar_altitude("2005-01-01 14:00:00+0100") == pytest.approx(59.75,0.05)
    # and azimut
    sevilla.get_solar_azimut("2005-01-01 14:00:00+0100") == pytest.approx(65.67,0.05)
    