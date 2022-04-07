"""
This module contains the test for the Consumer class
"""
from shipcal.energy_consumer import Consumer

from pytest import approx

def test_addup_toannualenery():
    """ 
    Check that the demand vector adds up to the provided annual_demand
    in the profile dictionary.
    """
    demand_profile = {
        'annual_demand': 20000, # [kWh]
        'week_profile':[1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7],
        'monthly_profile': [1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12],
        'day_profile':[0,24]
    }
    company_consumer = Consumer(demand_profile=demand_profile)
    assert company_consumer.demand_vector.sum() == approx(demand_profile["annual_demand"]), \
        "The demand vector does not add up to the provided annual demand"

    demand_profile = {
        'annual_demand': 20000, # [kWh]
        'week_profile':[1/5, 1/5, 1/5, 1/5, 1/5, 0, 0],
        'monthly_profile': [1/11,1/11,1/11,1/11,1/11,1/11,1/11,1/11,1/11,1/11,1/11,0],
        'day_profile':[8,20]
    }
    company_consumer = Consumer(demand_profile=demand_profile)
    assert company_consumer.demand_vector.sum() == approx(demand_profile["annual_demand"]), \
        "The demand vector does not add up to the provided annual demand"
