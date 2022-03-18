"""
This file contains the main class SHIPcal which contains the logic
to connect the elements together
"""

from weather import Weather
from energy_consumer import Consumer
from collectors import Collector

class SHIPcal:
    """
    This class is a simulation, it is meant to manage the loop to simulate
    each step through the elements in the simulation array.
    """
    def __init__(self, company, elements_array, colector, weather):
        self.company = company
        self.elements_array = elements_array
        self.colector = colector
        self.weather = weather

    def simulate(self):
        steps = len(self.company.demand)

if __name__ == "__main__":
    sigma_aldrich = Consumer("./tests/demand_sin.csv")
    sevilla = Weather("./TMYs/Sevilla.csv")
    challenger = Collector()
    simulation = SHIPcal(sigma_aldrich, [], challenger, sevilla)
