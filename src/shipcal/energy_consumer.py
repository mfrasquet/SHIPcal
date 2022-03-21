"""
This file contains the classes that define the energy consumers
in the simulation.
"""
from pathlib import Path

import pandas as pd

from shipcal.elements import Element


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

        if location_csv:
            self._demand_vector, self._step_resolution = self.read_demand_file(
                location_csv, step_resolution
            )
        # TODO Add demand creator functions
        # elif demand_profile:
        #     self._demand_vector, self._step_resolution = self.create_demand_vector(
        #         demand_profile, step_resolution
        #     )
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

    def read_demand_file(self, location_csv, step_resolution):
        """
        Receives the path to the location of a csv. The csv is assumed to
        contain equally time spaced records of the energy consumption of
        the process trough year. Redefines the step_resolution if not
        provided

        Returns:
            - demand_vector
            - step_resolution
        """

        # Read file
        location = Path(location_csv)
        if not location.exists():
            raise ValueError(f"Path to file {location} does not exists.")
        demand_vector = pd.read_csv(location, names=["demand"])
        if step_resolution:
            # TODO add resample of csv file if step_resolution is provided
            step_resolution = pd.tseries.frequencies.to_offset("1h")
        else:
            # Sets the step resolution.]
            year_mins = 365 * 24 * 60
            step_mins = year_mins / len(demand_vector)
            if not step_mins % 1 == 0:
                raise ValueError("File exceeds max resolution of 1min")
            step_mins = int(step_mins)
            step_resolution = pd.tseries.frequencies.to_offset(f"{step_mins}min")

        return demand_vector, step_resolution

    # def create_demand_vector(self, demand_profile, step_resolution = None):
    #     """
    #     Receives a dictionary with the annual demand and monthly, week,
    #     and daily consumption profile to build the demand vector. If a
    #     step_resolution smaller than hourly is provided the demand though
    #     each hour is uniformily distributed. The demand_profile dictionary
    #     has the following format
    #     demand_profile = {
    #         'annual_demand': 20000, # [kWh]
    #         'monthly_profile': [usage_ratio_January,usage_ratio_Feb, ... ], # [-]
    #         'week_profile': [usage_ratio_Monday, usage_ratio_Tuesday, ... ], # [-]
    #         'day_profile':[hour_start, hour_end], # [-]
    #     }
    #     And example of the
    #     demand_profile dictionary where the demand is constant trough the
    #     whole year is:
    #     demand_profile = {
    #         'annual_demand': 20000 # [kWh],
    #         'monthly_profile': [
    #              1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12
    #          ], # [-]
    #         'week_profile':20000 [1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7], # [-]
    #         'day_profile':[0,24] # [-]
    #     }
    #     Returns:
    #         - demand_vector
    #         - step_resolution
    #     """
    #     #days_in_the_month[month_number]=how many days are in the month number "month_number"
    #     days_in_the_month=[31,28,31,30,31,30,31,31,30,31,30,31]
    #     monthly_demand = demand_profile["monthly_profile"]*demand_profile["annual_demand"]
    #     hourly_demand = []
    #     for n_month in range(12):
    #         for ny_day in range(days_in_the_month[n_month]):
    #     demand_vector = None
    #     step_resolution = None
    #     return demand_vector, step_resolution


if __name__ == "__main__":
    demand_file_csv = Path("./tests/demand_sin.csv")
    sigma_aldrich = Consumer(demand_file_csv)
