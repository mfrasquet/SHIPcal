"""
This module contains the definition of the Weather class, used
to model the weather at the provided location from an hourly TMY.
"""
from pathlib import Path
from typing import Dict, Tuple, Union
import datetime

import numpy as np
import pandas as pd

from pvlib.iotools import read_tmy3, read_tmy2
from pvlib.solarposition import get_solarposition, declination_spencer71


def read_explorador_solar_tmy(file_loc: str) -> Tuple[pd.DataFrame, Dict[str, Union[str, float]]]:
    """
    Reads tmy exported from the Chilean explorador solar app.

    Parameters
    ----------
    file_loc : Path | str
        Path to file.

    Returns
    -------
    tmy_data : pd.DataFrame
        Pandas dataframe including hourly weather data (tmy).
    metadata : Dict
        Dictionary containing location data as Name, latitude,
        longitude, altitude and TZ
    """

    metadata_line = pd.read_csv(file_loc, nrows=1)
    tmy_data = pd.read_csv(file_loc, skiprows=2)
    metadata = dict(
        Name=metadata_line["City"][0],
        latitude=float(metadata_line["Latitude"]),
        longitude=float(metadata_line["Longitude"]),
        altitude=float(metadata_line["Elevation"]),
        TZ=float(metadata_line["Time Zone"])
    )
    # get the date column as a pd.Series of numpy datetime64
    data_index = pd.DatetimeIndex(
        pd.to_datetime(
            tmy_data.loc[:, ["Year", "Month", "Day", "Hour", "Minute"]]
        )
    )
    tmy_data.index = data_index
    tmy_data.tz_localize(int(metadata["TZ"] * 3600))
    columns_names = {
        "GHI": "GHI (W/m^2)",
        "DNI": "DNI (W/m^2)",
        "DHI": "DHI (W/m^2)",
        "Tdry": "Dry-bulb (C)",
        "Tdew": "Dew-point (C)",
        "RH": "RHum (%)",
        "Pres": "Pressure (mbar)",
        "Wspd": "Wspd (m/s)",
        "Wdir": "Wdir (degrees)",
    }
    tmy_data.rename(columns=columns_names, inplace=True)
    return tmy_data, metadata


class Weather:
    """
    This class handles the TMY file reads and prepare the variables to
    return the weather state at any hour of the simulation. Assumes the
    tmy file has a hourly resolution. The resolution of the hourly tmy
    readed can be extended with the step_resolution parameter. Solar time
    is assumed, if your tmy has official local time use local_time=True
    in the constructor. The following units are assumed

    Date (MM/DD/YYYY)
    Time (HH:MM)
    ETR (W/m^2)
    ETRN (W/m^2)
    GHI (W/m^2)
    GHI source
    GHI uncert (%)
    DNI (W/m^2)
    DNI source
    DNI uncert (%)
    DHI (W/m^2)
    DHI source
    DHI uncert (%)
    GH illum (lx)
    GH illum source
    Global illum uncert (%)
    DN illum (lx)
    DN illum source
    DN illum uncert (%)
    DH illum (lx)
    DH illum source
    DH illum uncert (%)
    Zenith lum (cd/m^2)
    Zenith lum source
    Zenith lum uncert (%)
    TotCld (tenths)
    TotCld source
    TotCld uncert (code)
    OpqCld (tenths)
    OpqCld source
    OpqCld uncert (code)
    Dry-bulb (C)
    Dry-bulb source
    Dry-bulb uncert (code)
    Dew-point (C)
    Dew-point source
    Dew-point uncert (code)
    RHum (%)
    RHum source
    RHum uncert (code)
    Pressure (mbar)
    Pressure source
    Pressure uncert (code)
    Wdir (degrees)
    Wdir source
    Wdir uncert (code)
    Wspd (m/s)
    Wspd source
    Wspd uncert (code)
    Hvis (m)
    Hvis source
    Hvis uncert (code)
    CeilHgt (m)
    CeilHgt source
    CeilHgt uncert (code)
    Pwat (cm)
    Pwat source
    Pwat uncert (code)
    AOD (unitless)
    AOD source
    AOD uncert (code)
    Alb (unitless)
    Alb source
    Alb uncert (code)
    Lprecip depth (mm)
    Lprecip quantity (hr)
    Lprecip source
    Lprecip uncert (code)
    """

    def __init__(
        self, location_file: Union[Path, str], step_resolution: str = "1h",
        mofdni: float = 1.0, local_time: bool = False
    ) -> None:

        self.mofdni = mofdni
        self.location_file = location_file
        self._step_resolution = step_resolution
        self._data_h, self._metadata = self.read_file()

        # Creates an empty frame which will hold only the used weather vars
        # with a solar time index
        self._data = pd.DataFrame()

        # Distributes or interpolate property accordingly
        self._data["DNI"] = self.resample_distribute(self._data_h["DNI"])
        self._data["GHI"] = self.resample_distribute(self._data_h["GHI"])
        self._data["DryBulb"] = self.resample_interpolate(self._data_h["DryBulb"])
        self._data["RHum"] = self.resample_interpolate(self._data_h["RHum"])
        self._data["Wspd"] = self.resample_interpolate(self._data_h["Wspd"])

        # Computes the grid water temperature
        self._data["grid_temp"] = self.resample_interpolate(
            pd.Series(self._compute_grid_temp(), index=self._data_h.index)
        )

        # Column of julian day
        self.local_date_0 = self._data.index[0]
        self._data["julian_day"] = (self._data.index - self.local_date_0).days + 1

        # Converts self._data index from local time to solar time
        self._data["solar_time"] = self._data.index
        if local_time:
            self._data["solar_time"] = self._data["solar_time"].apply(self._conv_local_to_solar)

        solarpos_df = get_solarposition(self._data["solar_time"],  self.lat, self.lon)
        self._data = pd.concat([self._data, solarpos_df], axis=1)

        # Computes and stores the declination
        self._data["declination"] = self._data["julian_day"].apply(declination_spencer71)

        del self.local_date_0
        del self._data_h

    def _add_dummy_fields_tmy2(self) -> None:
        """
        If the tmy2 has missing fields in metadata line adds them with
        'dummy' for pvlib readthem properly.

        This method modifies the file, in self.location_file receives
        no parameters and returns nothing.
        """

        with open(self.location_file, "r",) as orig_tmy2:
            metaraw = orig_tmy2.readline()
            metaraw = " ".join(metaraw.split()).split(" ")
            if len(metaraw) < 11:
                n_missing_fields = 11 - len(metaraw)
                # Search for S or N index
                i = -1
                for item in metaraw:
                    if item == "S" or item == "N":
                        break
                    i += 1
                dummy_list = ["dummy"] * n_missing_fields
                metaraw = metaraw[:i] + dummy_list + metaraw[i:]
                metaraw = " ".join(metaraw)
                modified_location_list = str(self.location_file).split(".")
                modified_location = "".join(
                    modified_location_list[:-1] + ["_mod."] + modified_location_list[-1:]
                )
            # Write into new file
            mod_file = open(modified_location, "w")
            mod_file.write(metaraw)
            mod_file.write(orig_tmy2.read())
            mod_file.close()
            self.location_file = modified_location

    def _conv_local_to_solar(self, local_datetime: datetime.datetime) -> datetime.datetime:
        """
        Computes the local solar datetime from the official local datetime.

        Parameters
        ----------
        local_datetime : datetime.datetime
            Local official/civil time.

        Returns
        -------
        datetime.datetime
            Local real solar time.
        """

        local_longitude = self._metadata["longitude"]
        standard_longitude = self._metadata["TZ"] * 15

        # Get number of day in the calendar
        julian_days = (local_datetime - self.local_date_0).days + 1

        # "equation of time" operations
        b = np.radians((julian_days - 81) * (360 / 365))
        equation_time = 9.87 * (np.sin(2 * b)) - 7.53 * (np.cos(b))\
            - 1.5 * (np.sin(b))

        # Create correction factor timedelta
        correction_factor = datetime.timedelta(
            minutes=4 * (local_longitude - standard_longitude) + equation_time
        )

        # Structure of equation
        local_solar_time = local_datetime + correction_factor

        return local_solar_time

    def read_file(self) -> Tuple[pd.DataFrame, Dict[str, Union[str, float]]]:
        """
        Gets file location, reads its content and stores its data in
        this class variables.

        Modify this method if your TMY does not have the standard
        format. It should return the same dataframe format.

        Returns
        -------
        Tuple[pd.DataFrame, Dict[str, Union[str, float]]]
            Tuple containg a pandas dataframe with the tmy data and a
            tuple with info about the location (name, lat, lon, altitude, tz)
        """
        file_ext = self.location_file.as_posix().split(".")[-1]
        if file_ext == "csv":
            try:
                data, metadata = read_tmy3(self.location_file)
            except pd.errors.ParserError:
                data, metadata = read_explorador_solar_tmy(self.location_file)
        elif file_ext == "tm2":
            self._add_dummy_fields_tmy2()
            data, metadata = read_tmy2(self.location_file)

        return data, metadata

    def resample_interpolate(self, prop_series: pd.Series) -> pd.Series:
        """
        This method receives a time series based property and a step
        resolution description and returns a time series with this step
        resolution where each entry is an interpolation of the the two
        nearest hourly entries.

        Time descriptors examples

        1h = 1 hour steps
        10min = 10 minutes steps
        5T = 5 minutes steps

        Parameters
        ----------
        prop_series : pd.Series
            Series of property to interpolate. Must have a datetime index.

        Returns
        -------
        pd.Series
            Interpolated panda series of the property. Datetime Index is updated
        """

        return prop_series.resample(self.step_resolution).interpolate()

    def resample_distribute(self, prop_series: pd.Series) -> pd.Series:
        """
        This method receives a time series based property and a step
        resolution description and returns a time series with this step
        resolution where the sum of all entries between two consecutive
        hours adds up to the original hourly entry.

        If the time step is dh and the original value in the hourly array
        is v at h_n then

        v=sum from h_{n-1} to h_n of v_i

        Time descriptors examples

        1h = 1 hour steps
        10min = 10 minutes steps
        5T = 5 minutes steps

        Parameters
        ----------
        prop_series : pd.Series
            Series of property to distributed. Must have a datetime index.

        Returns
        -------
        pd.Series
            Distributed panda series of the property. Datetime Index is updated
        """

        distribution_norm = pd.tseries.frequencies.to_offset(self.step_resolution)\
            / pd.Timedelta('1h')
        return prop_series.resample(self.step_resolution).bfill() * distribution_norm

    def interpolate_prop(self, h_id: float, prop_array: pd.Series) -> float:
        """
        Interpolate the property to a fractional index of the array

        Parameters
        ----------
        h_id : float
            Noninteger index
        prop_array : pd.Series
            Series of property to interpolate. Must have a datetime index.

        Returns
        -------
        float
            Interpolated property value at h_id.
        """
        h_floor = int(np.floor(h_id))
        h_ceil = int(np.ceil(h_id))
        h_change = h_ceil - h_floor
        if h_change == 0:
            return prop_array[h_floor]
        dprop = prop_array[h_ceil] - prop_array[h_floor]

        prop = prop_array[h_floor] + (dprop / h_change) * (h_id - h_floor)

        return prop

    def distribute_prop(self, h_id: float, prop_array: pd.Series) -> float:
        """
        This method distributes the property in prop_array[h] through
        the interval [h-1, h] uniformely.

        Parameters
        ----------
        h_id : float
            Noninteger index
        prop_array : pd.Series
            Series of property to distribute. Must have a datetime index.

        Returns
        -------
        float
            Distributed property value at h_id.
        """
        h_ceil = int(np.ceil(h_id))
        h_floor = int(np.floor(h_id))
        val = (prop_array[h_ceil]) * (h_id - h_floor)
        return val

    @property
    def step_resolution(self):
        """
        [-] This property is the number of entries in the array of
        the properties.
        """
        return self._step_resolution

    @property
    def tz_loc(self):
        """ [-] Int. Timezone of the location in simulation """
        return self._metadata["TZ"]

    @property
    def elev(self):
        """ [m] Float. Height above sea level """
        return self._metadata["altitude"]

    @property
    def lat(self):
        """ [°] Float. Latitude of location in simulation """
        return self._metadata["latitude"]

    @property
    def lon(self):
        """ [°] Float. Longitude of location in simulation. """
        return self._metadata["longitude"]

    @property
    def location_file(self):
        """ String. Location of the TMY file currently used """
        return self._location_file

    @location_file.setter
    def location_file(self, path_to_file):
        self._location_file = Path(path_to_file)
        if not self.location_file.exists():
            raise ValueError(f"No such file {path_to_file}.")

    def get_dni(self, hour=None):
        """
        Returns DNI array or the hth DNI in the array. hour can be nonninteger.
        """
        if hour:
            return self.distribute_prop(hour, self._data["DNI"])
        else:
            return self._data["DNI"]

    dni = property(
        get_dni,
        doc=""" [W/m^2] Hourly array. Direct Normal Irradiation (dni). """
    )

    def get_ghi(self, hour=None):
        """ [W/m^2] Hourly array. Global Horizontal Irradiation (ghi_ghi). """

        if hour:
            return self.distribute_prop(hour, self._data["GHI"])
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
            return self.interpolate_prop(hour, self._data["DryBulb"])
        else:
            return self._data["DryBulb"]

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
            return self.interpolate_prop(hour, self._data["grid_temp"])
        else:
            return self._data["grid_temp"]

    def _compute_grid_temp(self) -> np.ndarray:
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
        ratio = 0.22 + 0.0056 * (amb_temp_mean - 6.67)
        lag = 1.67 - 0.56 * (amb_temp_mean - 6.67)

        grid_temps = []

        for day in range(365):
            # The hourly year array is built by the temperature
            # calculated for the day printed 24 times for each day
            # This was taken from TRNSYS documentation.
            grid_temps += [(
                (amb_temp_mean + offset) +
                ratio * (amb_temp_max / 2) * np.sin(
                    np.radians(-90 + (day - 15 - lag) * 360 / 365)
                )
            )] * 24
        return np.array(grid_temps)

    grid_temp = property(
        get_grid_temp,
        doc=""" [°C] Hourly array. Water temperature from grid. """
    )

    def get_humidity(self, hour=None):
        """
        Returns ambient relative humidity array or the hth humidity
        in the array. hour can be nonninteger.
        """
        if hour:
            return self.interpolate_prop(hour, self._data["RHum"])
        else:
            return self._data["RHum"]

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
            return self.interpolate_prop(hour, self._data["Wspd"])
        else:
            return self._data["Wspd"]

    wind_speed = property(
        get_wind_speed,
        doc=""" [m/s] Hourly array. Wind speed. """
    )

    def get_solar_altitude(self, hour=None):
        """
        Returns solar altitude array or the hth altitude in the array.
        hour can be nonninteger.
        """
        if hour:
            return self.interpolate_prop(hour, self._data["elevation"])
        else:
            return self._data["elevation"]

    solar_altitude = property(
        get_solar_altitude,
        doc=""" [°] Altitude from the astronomical horizon."""
    )

    def get_solar_azimut(self, hour=None):
        """
        Returns solar azimuth array or the hth azimuth in the array.
        hour can be nonninteger.
        """
        if hour:
            return self.interpolate_prop(hour, self._data["azimuth"])
        else:
            return self._data["azimuth"]

    solar_azimut = property(
        get_solar_azimut,
        doc=""" [°] Solar azimuth."""
    )

    def get_solar_declination(self, hour=None):
        """
        Returns declination array or the hth declination in the array.
        hour can be nonninteger.
        """
        if hour:
            return self.interpolate_prop(hour, self._data["declination"])
        else:
            return self._data["declination"]

    declination = property(
        get_solar_declination,
        doc=""" [°] Earth's declination."""
    )


if __name__ == "__main__":
    sevilla_file = Path(
        "./src/shipcal/weather/data/Sevilla.csv"
    )
    sevilla = Weather(sevilla_file, "10min")

    print(sevilla.amb_temp.mean())
    for i in range(11):
        print(sevilla.amb_temp[i])
