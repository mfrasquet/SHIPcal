"""
This module contains the definition of the Weather class, used
to model the weather at the provided location from an hourly TMY.
"""

from pathlib import Path

import numpy as np

class Weather:
    """
    This class handles the TMY file reads and prepare the variables to
    return the weather state at any hour of the simulation.
    Assumes solar time.
    """

    def __init__(self, location_file, mofdni=1):
        self.mofdni = mofdni
        self.location_file = location_file
        [
            self._lat, self._lon, self._elev,
            self._tz_loc, self._dni, self._ghi,
            self._amb_temp, self._humidity, self._wind_speed
        ] = self.read_file()
        self.set_grid_temp()

    def read_file(self):
        """
        Gets file location, reads its content and stores its data in
        this class variables.

        Modify this method if your TMY does not have the standard format.
        """

        with open(self.location_file, "r", encoding="utf-8") as tmy:
            tmy.readline()
            location_data = tmy.readline()
        lat, lon, elev, tz_loc = location_data.split()

        tmy = np.loadtxt(self.location_file, skiprows=4)

        dni = tmy[:,5]*self.mofdni
        ghi_ghi = tmy[:,6]*self.mofdni
        amb_temp = tmy[:,7]
        humidity = amb_temp
        wind_speed = humidity
        return lat, lon, elev, tz_loc, dni, ghi_ghi, amb_temp, humidity, wind_speed

    def interpolate_prop(self, h_id, prop_array):
        """ Interpolate the property to a fractional index of the array """
        h_floor = int(np.floor(h_id))
        h_ceil = int(np.ceil(h_id))
        h_change = h_ceil-h_floor
        if h_change == 0:
            return prop_array[h_floor]
        dprop = prop_array[h_ceil]-prop_array[h_floor]

        prop = prop_array[h_floor] + (dprop/h_change)*(h_id-h_floor)

        return prop

    @property
    def tz_loc(self):
        """ [-] Int. Timezone of the location in simulation """
        return self._tz_loc

    @property
    def elev(self):
        """ [m] Float. Height above sea level """
        return self._elev

    @property
    def lat(self):
        """ [°] Float. Latitude of location in simulation """
        return self._lat

    @property
    def lon(self):
        """ [°] Float. Longitude of location in simulation. """
        return self._lon

    @property
    def location_file(self):
        """ String. Location of the TMY file currently used """
        return self._location_file

    @location_file.setter
    def location_file(self, path_to_file):
        self._location_file = Path(path_to_file)
        if not self.location_file.exists():
            raise ValueError(f"No such file {path_to_file}.")
        self.read_file()

    def get_dni(self, hour=None):
        """
        Returns DNI array or the hth DNI in the array. hour can be nonninteger.
        """
        if hour:
            return self.interpolate_prop(hour, self._dni)
        else:
            return self._dni

    dni = property(
        get_dni,
        doc=""" [W/m^2] Hourly array. Direct Normal Irradiation (dni). """
    )

    def get_ghi(self, hour=None):
        """ [W/m^2] Hourly array. Global Horizontal Irradiation (ghi_ghi). """
        if hour:
            return self.interpolate_prop(hour, self._ghi)
        else:
            return self._ghi

    ghi_ghi = property(
        get_ghi,
        doc=""" [W/m^2] Hourly array. Global Horizontal Irradiation (ghi_ghi). """
    )

    def get_amb_temp(self, hour=None):
        """
        Returns the ambient temperature array or the hth temperature
        in the array. hour can be nonninteger.
        """
        if hour:
            return self.interpolate_prop(hour, self._amb_temp)
        else:
            return self._amb_temp

    amb_temp = property(
        get_amb_temp,
        doc=""" [°C] Hourly array. Ambient temperature. """
    )

    def get_grid_temp(self, hour=None):
        """
        Returns grid temperature array or the hth temperature in the array.
        hour can be nonninteger.
        """
        if hour:
            return self.interpolate_prop(hour, self._grid_temp)
        else:
            return self._grid_temp

    def set_grid_temp(self):
        """
        This method computes the water temperature in grid from
        the ambient temperature property.
        """
        amb_temp_mean = self.amb_temp.mean()
        amb_temp_max = self.amb_temp.max()

        # The offset, lag, and ratio values were obtained by fitting data
        # compiled by Abrams and Shedd [8], the FloridaSolar Energy
        # Center [9], and Sandia National Labs
        offset = 3
        ratio = 0.22 + 0.0056*(amb_temp_mean - 6.67)
        lag = 1.67 - 0.56*(amb_temp_mean - 6.67)

        grid_temps=[]

        for day in range(365):
            # The hourly year array is built by the temperature
            # calculated for the day printed 24 times for each day
            # This was taken from TRNSYS documentation.
            grid_temps+=[(
                    (amb_temp_mean+offset)+
                    ratio*(amb_temp_max/2)*np.sin(
                            np.radians(-90+(day-15-lag)*360/365)
                        )
                )]*24
        self._grid_temp = np.array(grid_temps)

    grid_temp = property(
        get_grid_temp,
        set_grid_temp,
        doc=""" [°C] Hourly array. Water temperature from grid. """
    )

    def get_humidity(self, hour=None):
        """
        Returns ambient relative humidity array or the hth humidity
        in the array. hour can be nonninteger.
        """
        if hour:
            return self.interpolate_prop(hour, self._humidity)
        else:
            return self._humidity

    humidity = property(
        get_humidity,
        doc=""" [-] Hourly array. Relative humidity. """
    )

    def get_wind_speed(self, hour=None):
        """
        Returns wind speed array or the hth speed in the array.
        hour can be nonninteger.
        """
        if hour:
            return self.interpolate_prop(hour, self._wind_speed)
        else:
            return self._wind_speed

    wind_speed = property(
        get_wind_speed,
        doc=""" [m/s] Hourly array. Wind speed. """
    )

if __name__ == "__main__":
    sevilla_file = Path(
        "./TMYs/Sevilla.csv"
    )
    sevilla = Weather(sevilla_file)

    print(sevilla.amb_temp.mean())
    print(sevilla.amb_temp[2])
    print(sevilla.get_amb_temp(2.1))
    print(sevilla.get_amb_temp(2.5))
    print(sevilla.get_amb_temp(2.9))
    print(sevilla.get_amb_temp(3))
