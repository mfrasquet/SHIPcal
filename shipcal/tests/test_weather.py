"""
This module contains the test for the Weather class
"""
import unittest

from shipcal.weather import Weather

class TestWeather(unittest.TestCase):
    """ Tests on weather class. Readed and computed data """

    def test_read_tmy3(self):
        """ Check that tmy3 format is bein read correctly """
        sevilla_tmy3_loc = "./tests/TMYs/Sevilla.csv"
        sevilla = Weather(sevilla_tmy3_loc)
        self.assertEqual(sevilla.lat, 37.410)

if __name__ == '__main__':
    unittest.main()
