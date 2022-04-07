"""
This file contains the classes that define the energy consumers
in the simulation.
"""
from pathlib import Path
import datetime

import pandas as pd
import numpy as np

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
        elif demand_profile:
            self._demand_vector, self._step_resolution = self.create_demand_vector(
                demand_profile, step_resolution
            )
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

    def create_demand_vector(self, demand_profile, step_resolution=None,  year=2022):
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
                'day_profile':[0,24]}
        step_resolution : String | Float, optional
            Stablishes a resolution different than hourly. If receives a String
            it will try to convert it using, by default None
        year : int, optional
            The current year in simulation, by default 2022

        Returns
        -------
        _type_
            _description_
        """

        # days_in_the_month[month_number]=how many days are in the month number "month_number"
        days_in_the_month = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

        # weeks_in_the_month[month_number]=how many weeks are in the month number "month_number"
        weeks_in_the_month = days_in_the_month / 7

        # saves 'week_profile' and 'day_profile' as numpy arrays
        monthly_profile = np.array(demand_profile["monthly_profile"])
        week_profile = np.array(demand_profile["week_profile"])
        day_profile = np.array(demand_profile["day_profile"])

        # monthly_demand is the the distribuiton of the annual demand through the months,
        # define by the monthly profile
        monthly_demand = monthly_profile * demand_profile["annual_demand"]

        # Creates the array "hour_profile".
        # This array has 24 entrace that uniformily distribute the hourly demand of all days
        hour_profile = np.zeros(24)
        for i in range(day_profile[0], day_profile[1]):
            hour_profile[i] = 1 / (day_profile[1] - day_profile[0])

        # Creates an empty list that will save the hourly demand
        demand_vector = []

        for n_month in range(12):

            # Calculates the weekly_demand based on the monthly demand and
            # the number of weeks in each month
            weekly_demand = np.array(monthly_demand[n_month]) / weeks_in_the_month[n_month]

            for ny_day in range(days_in_the_month[n_month]):

                # Calculates wich day of the week correspondes a certain date
                day_of_the_week = datetime.date(year, (n_month + 1), (ny_day + 1)).weekday()

                # Calculates the demand of each day based on the weekly demand and
                # week profile for a certain day of the week
                day_demand = weekly_demand * week_profile[day_of_the_week]

                # Saves the demand of each hour based on the day demand and
                # the hour profile distribution
                for hour in range(24):
                    demand_vector.append(day_demand * hour_profile[hour])

        # If a step_resolution is declared then the demand through each hour is
        # uniformily distributed
        if step_resolution:
            time_step = int(60 / step_resolution)
            demand_vector_aux = []
            for i in range(len(demand_vector)):
                for j in range(time_step):
                    demand_vector_aux.append(demand_vector[i] / time_step)

            demand_vector = demand_vector_aux

        return (np.array(demand_vector), step_resolution)


if __name__ == "__main__":
    # demand_file_csv = Path("./tests/demand_sin.csv")
    # sigma_aldrich = Consumer(demand_file_csv)
    demand_profile = {
                'annual_demand': 20000, # [kWh]
                'monthly_profile': [1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12],
                'week_profile':[1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7],
                'day_profile':[0,24]}
    c = Consumer(demand_profile=demand_profile)
