"""
This file contains the classes that define the energy consumers
in the simulation.
"""
from typing import Dict, Union
from pathlib import Path

import pandas as pd
import numpy as np

from shipcal.elements import Element


MINS_YEAR = 365 * 24 * 60


def resample_property(step_resolution: str, property_df_orig: pd.DataFrame) -> pd.DataFrame:
    """
    This function receives a DataFrame with a TimeIndex and resamples it
    to a datagrame with a frequency given by the step resolution. The
    property is uniformily distributed trough its higher resolution entries.
    In this way if you initialy had

    df_orig:
        2022-01-01 01:00:00   1.917437
        2022-01-01 02:00:00   0.000000

    you will obtain
    df_resampled:
        2022-01-01 00:05:00  0.159786
        2022-01-01 00:10:00  0.159786
        2022-01-01 00:15:00  0.159786
        2022-01-01 00:20:00  0.159786
        2022-01-01 00:25:00  0.159786
        2022-01-01 00:30:00  0.159786
        2022-01-01 00:35:00  0.159786
        2022-01-01 00:40:00  0.159786
        2022-01-01 00:45:00  0.159786
        2022-01-01 00:50:00  0.159786
        2022-01-01 00:55:00  0.159786
        2022-01-01 01:00:00  0.159786
        2022-01-01 02:05:00  0.000000

    Note that 0.159786 * 12 = 917437

    Parameters
    ----------
    step_resolution : str
        Offset alias. It must follow the format in
        https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
        for example 5 min. The max resolution is 1 min.
    property_df_orig : pd.DataFrame
        A DataFrame with a TimeIndex of the property to be distributed.

    Returns
    -------
    pd.DataFrame
        A DataFrame whith step_resolution as new frequency in the TimeIndex.
        The property is distributed.
    """

    # Obtain dateoffset from string
    step_resolution_dateoffset = pd.tseries.frequencies.to_offset(step_resolution)

    # Copies original dataframe to a new variable for manipulation
    distributed_prop_df = property_df_orig.copy()

    # Shifts the index to start to the hour 0 of the year + the step_resolution
    distributed_prop_df.index = \
        distributed_prop_df.index - distributed_prop_df.index.freq \
        + step_resolution_dateoffset

    # Appends the last row to the end of the data fram so the new dataframe
    # still ends at yyy-12-31 24:00
    last_row = pd.DataFrame(
        {distributed_prop_df.columns[0]: distributed_prop_df.iloc[-1, 0]},
        index=[property_df_orig.index[-1]]
    )
    distributed_prop_df = pd.concat([distributed_prop_df, last_row])

    # Resamples and fills forward the new rows
    distributed_prop_df = distributed_prop_df.resample(step_resolution).ffill()

    # Computes the normalization for the distribution.
    distribution_norm = step_resolution_dateoffset \
        / property_df_orig.index.freq
    distributed_prop_df = distributed_prop_df * distribution_norm
    return distributed_prop_df


class Consumer(Element):
    """
    This class creates objects that consumes the energy produced by the
    colector. It can create a demand profile from:

        - A csv file where the sum of all the entries is assumed to be
    the annual energy demand in [kWh]. This will also overwrite the step
    resolution of the simulation to match the number of entries in the
    file, unless the step resolution is explicitly indicated.
        - A dictionary of monthly, weekly and yearly demand profiles [-]
    and a total annual demand in [kWh]. An hourly step is assumed except
    a different step is explicitly indicated.
    """

    def __init__(
        self, location_csv=None, demand_profile=None, step_resolution=None,
        boiler_efficiency=0.8
    ):
        super().__init__()

        self.boiler_efficiency = boiler_efficiency
        self._step_resolution = step_resolution

        if location_csv:
            self._demand_vector = self.read_demand_file(location_csv)
        elif demand_profile:
            self._demand_vector = self.create_demand_vector(demand_profile)
        else:
            raise ValueError(
                "Missing demand file (location_csv) or demand_profile dict"
            )
        self._annual_demand = self._demand_vector.sum()

    @property
    def demand_vector(self):
        """ Returns the demand vector """
        return self._demand_vector

    @property
    def boiler_efficiency(self):
        """
            [-] Boiler efficiency. This value is used to compute how much
            energy does the process actually needs.
        """
        return self._boiler_efficiency

    @boiler_efficiency.setter
    def boiler_efficiency(self, val):
        self._boiler_efficiency = val

    @property
    def step_resolution(self):
        """ [-] String that represents the step resolution of the demand """
        return self._step_resolution

    def read_demand_file(self, location_csv: str) -> pd.DataFrame:
        """
        Receives the path to the location of a csv. The csv is assumed to
        contain equally time spaced records of the energy consumption of
        the process trough year. Redefines the step_resolution if not
        provided
        """

        # Read file
        location = Path(location_csv)
        if not location.exists():
            raise ValueError(f"Path to file {location} does not exists.")
        demand_vector = pd.read_csv(location, names=["demand"])

        # Get current datetime index
        periods = demand_vector.count()["demand"]
        freq = str(MINS_YEAR // periods) + "min"
        demand_vector.index = pd.date_range(
            start="2022-01-01 01:00", periods=periods, freq=freq
        )

        if not self._step_resolution:
            self._step_resolution = freq
        else:
            demand_vector = resample_property(self.step_resolution, demand_vector)

        return demand_vector

    def create_demand_vector(self, demand_profile: Dict[str, Union[list, float]]) -> pd.DataFrame:
        """
        Receives a dictionary with the annual demand and monthly, week,
        and daily consumption profile to build the demand vector. If a
        step_resolution smaller than hourly is provided the demand through
        each hour is uniformily distributed.

        Parameters
        ----------
        demand_profile : Dictionary
            It is the dictionary with the demand profile. It has
            the following format

            demand_profile = {
                'annual_demand': 20000, # [kWh]
                'monthly_profile': [usage_ratio_January,usage_ratio_Feb, ... ],
                'week_profile': [usage_ratio_Monday, usage_ratio_Tuesday, ... ],
                'day_profile':[hour_start, hour_end]}

            An example of the
            demand_profile dictionary where the demand is constant trough the
            whole year is:
            demand_profile = {
                'annual_demand': 20000, # [kWh]
                'monthly_profile': [1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12],
                'week_profile':[1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7],
                'day_profile':[0,24]
            }

        Returns
        -------
        pd.DataFrame
            A data frame of with the demand column and timeindex with the
            frequency either hourly or specified by self.step_resolution.
        """

        days_in_month = np.array(
            [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        )
        h_ini = demand_profile["day_profile"][0]
        h_end = demand_profile["day_profile"][1]
        hour_percentage = 1 / (h_end - h_ini)
        day_vector = np.array([
            hour_percentage if (h < h_end and h >= h_ini) else 0
            for h in range(24)
        ])

        week_vector = np.array(demand_profile["week_profile"])

        energy_month_vector = np.array(demand_profile["monthly_profile"])\
            * demand_profile["annual_demand"]

        demand_vector = np.array([])
        for n_month, month_days in enumerate(days_in_month):
            energy_month = energy_month_vector[n_month]
            prev_months_days = days_in_month[:n_month].sum()
            for day in range(month_days):
                n_day = prev_months_days + day
                # Always starts on monday
                week_day = n_day % 7
                if week_vector[week_day] == 0:
                    demand_vector = np.append(
                        demand_vector, [0 for _ in range(24)]
                    )
                else:
                    demand_vector = np.append(
                        demand_vector, [
                            h_percentage * week_vector[week_day]
                            for h_percentage in day_vector
                        ]
                    )
            renormalization = demand_vector[prev_months_days * 24:].sum()
            demand_vector[prev_months_days * 24:] = energy_month \
                * demand_vector[prev_months_days * 24:] / renormalization

        demand_df = pd.DataFrame(
            {"demand": demand_vector},
            index=pd.date_range(
                start="2022-01-01 01:00", end="2023-01-01 00:00", freq="H"
            )
        )

        if not self._step_resolution:
            self._step_resolution = "1H"
        else:
            demand_df = resample_property(self.step_resolution, demand_df)

        return demand_df


if __name__ == "__main__":
    # demand_file_csv = Path("./tests/demand_sin.csv")
    # sigma_aldrich = Consumer(demand_file_csv)
    demand_profile = {
        'annual_demand': 20000,  # [kWh]
        'monthly_profile': [1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12, 1/12], # noqa
        'week_profile': [1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7], # noqa
        'day_profile': [0, 24]
    }
    c = Consumer(demand_profile=demand_profile)
