from typing import List
from shipcal.energy_consumer import Consumer


def get_generated_steam() -> List[float]:
    """
    This method converts the energy demand based on the demand profile
    into a steam flow.

    Returns
    -------
    List[float]
        Generated steam tons.
    """
    # This defines a consumer
    demand_profile = {
        "annual_demand": 20000,  # [kWh]
        "monthly_profile": [1 / 12] * 12,
        "week_profile": [1 / 7] * 7,
        "day_profile": [0, 24],
    }
    self = Consumer(demand_profile=demand_profile)

    # Your code here
    vapor_tons = self.demand_vector

    return vapor_tons


if __name__ == "__main__":
    generated_steam = get_generated_steam()
