"""
This module contains the test for the Weather class
"""
import pytest
from shipcal import Weather

import datetime

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
    sevilla_tmy3_loc = "./src/shipcal/weather/data/Sevilla.csv"
    # Should receive a parameter that states that the data is local time
    # to be converted
    sevilla = Weather(sevilla_tmy3_loc, local_time=True)

    # Consider at a location at the east of the greenwich tz
    # Then, for sevilla, the 12:00 h of the 01/01/2005 must be 10:33 +/- 30s
    civil_midday = sevilla.solar_time.loc["2005-01-01 12:00:00+0100"].to_pydatetime()
    expected_time = civil_midday.replace(hour=10, minute=32)
    assert (civil_midday - expected_time) < datetime.timedelta(seconds=30)

    # Consider daytime saving. Cannot be done without extra info in tmy
    # Then, for sevilla, the 12:00 h of the 30/03/2005 must be 09:31
    # civil_midday = sevilla.solar_time.loc["2005-03-30 12:00:00+0100"].to_pydatetime()
    # expected_time = civil_midday.replace(hour=9, minute=31)
    # assert (civil_midday - expected_time) < datetime.timedelta(seconds=30)

    # Consider a  location at the east of the greenwich tz
    rome_tmy2_loc = "./src/shipcal/weather/data/Roma_Ciampino_local_hour.tm2"
    rome = Weather(rome_tmy2_loc, local_time=True)
    civil_midday = rome.solar_time.loc["1905-12-12 11:00:00+0100"].to_pydatetime()
    expected_time = civil_midday.replace(hour=10, minute=56)
    assert (civil_midday - expected_time) < datetime.timedelta(seconds=30)

    # Consider a location in the southern hemisphere
    santiago_explorador_loc = "./src/shipcal/weather/data/Santiago_Chile_exlorador_solar.csv"
    santiago = Weather(santiago_explorador_loc, local_time=True)
    civil_midday = santiago.solar_time.loc["2007-02-02 11:00:00-0400"].to_pydatetime()
    expected_time = civil_midday.replace(hour=10, minute=3)
    assert (civil_midday - expected_time) < datetime.timedelta(seconds=30)

def test_sunposition():
    """
    Tests that the sun position is correct for few dates and locations
    """
    sevilla_tmy3_loc = "./src/shipcal/weather/data/Sevilla.csv"
    sevilla = Weather(sevilla_tmy3_loc)
    
    # The altitude in the step 13 (the 14 h) in Sevilla must be
    # This takes the datetime in the 16th element in the data
    assert sevilla.solar_elevation[13] == pytest.approx(29.13,0.05)
    # and azimut
    assert sevilla.solar_azimut[13] == pytest.approx(188.62,0.05)
    # I should be able to find the same altitude by entering a datetime
    # This should return the solar altitude in
    # the datetime '2005-01-01 17:00:00+0100'
    assert sevilla.solar_elevation.loc["2005-01-01 14:00:00+0100"] == pytest.approx(29.13,0.05)
    # and azimut
    assert sevilla.solar_azimut.loc["2005-01-01 14:00:00+0100"] == pytest.approx(188.62,0.05)
