"""
This module contains the test for the Weather class
"""
from shipcal import Weather


def test_read_tmy3():
    """ Check that tmy3 format is bein read correctly """
    sevilla_tmy3_loc = "/home/jaarpa/aProjects/solatom/SHIPcal/shipcal/weather/data/Sevilla.csv"
    sevilla = Weather(sevilla_tmy3_loc)
    assert sevilla.lat == 37.410
