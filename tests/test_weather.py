"""
This module contains the test for the Weather class
"""
from shipcal import Weather
from datetime import datetime

def test_read_tmy3():
    """ Check that tmy3 format is bein read correctly """
    sevilla_tmy3_loc = "src/shipcal/weather/data/Sevilla.csv"
    sevilla = Weather(sevilla_tmy3_loc)
    assert sevilla.lat == 37.410

def test_read_tmy2():
    """ Check that tmy2 files are being read properly """
    rome_tmy2_loc = "src/shipcal/weather/data/Roma_Ciampino_local_hour.tm2"
    rome = Weather(rome_tmy2_loc)
    assert rome.lat == 41.800

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
    assert sevilla_localtime.dni.loc["2005-01-01 10:33:00+0100"] == sevilla.dni[11]
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
    pass
    