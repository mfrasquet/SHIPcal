#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 17:49:37 2019

@author: miguel
"""
import numpy as np

def Turn_key(Energy_anual,Fuel_price,Boiler_eff,n_years_sim,Investment,OM_cost_year,incremento,Co2_savings):    
    #Inputs
#    Energy_anual=636632 #Energy produced annualy by the solar plant in kWh 
#    Fuel_price=0.04 #Price of fossil fuel in €/kWh
#    Boiler_eff=0.95 #Boiler efficiency to take into account the excess of fuel consumed
#    n_years_sim=20 #Number of years for the simulation
#    Investment=130000 #Initial investment in €
#    OM_cost_year=5000 #Cost of O&M/year in €
    
    #SIMULATION
    #Variable initiation
    fuelPrizeArray=np.zeros(n_years_sim)
    Energy_produced=np.zeros(n_years_sim)
    Energy_savings=np.zeros(n_years_sim)
    OM_cost=np.zeros(n_years_sim)
    Net_anual_savings=np.zeros(n_years_sim)
    Accumulated_savings=np.zeros(n_years_sim)
    FCF=np.zeros(n_years_sim)
    Acum_FCF=np.zeros(n_years_sim)
    num_LCOE=np.zeros(n_years_sim)
    denom_LCOE=np.zeros(n_years_sim)
    r=0.07
    
    for i in range(0,n_years_sim):
        if i==0:
            Energy_produced[i]=0
            Energy_savings[i]=0
            OM_cost[i]=0
            Net_anual_savings[i]=0
            Accumulated_savings[i]=0
            Acum_FCF[i]=-Investment
            FCF[i]=-Investment
            fuelPrizeArray[i]=Fuel_price
            num_LCOE[i]=Investment/((1+r)**i)
            denom_LCOE[i]=0
        else:
            
            Energy_produced[i]=Energy_anual
            Energy_savings[i]=Energy_anual*(Fuel_price*(1+incremento*(i-1)))/Boiler_eff + Co2_savings#€
            if i<=4:
                OM_cost[i]=0
            else:
                OM_cost[i]=OM_cost_year 
            num_LCOE[i]=OM_cost[i]/((1+r)**i)
            denom_LCOE[i]=Energy_produced[i]/((1+r)**i)
            Net_anual_savings[i]=Energy_savings[i]-OM_cost[i]
            Accumulated_savings[i]=Accumulated_savings[i-1]+Net_anual_savings[i]
            Acum_FCF[i]=Acum_FCF[i-1]+Net_anual_savings[i]
            FCF[i]=Net_anual_savings[i]
            fuelPrizeArray[i]=(Fuel_price*(1+incremento*(i-1)))

    LCOE=sum(num_LCOE)/sum(denom_LCOE)
    IRR10=100*np.irr(FCF[:10])
    IRR=100*np.irr(FCF)
    Amort_year=(Acum_FCF <= 0).sum()
    return [LCOE,IRR,IRR10,Amort_year,Acum_FCF,FCF,Energy_savings,OM_cost,fuelPrizeArray,Net_anual_savings]
    
def ESCO(priceReduction,Energy_anual,Fuel_price,Boiler_eff,n_years_sim,Investment,OM_cost_year,incremento,Co2_savings):    
    #Inputs
#    Energy_anual=636632 #Energy produced annualy by the solar plant in kWh 
#    Fuel_price=0.04 #Price of fossil fuel in €/kWh
#    Boiler_eff=0.95 #Boiler efficiency to take into account the excess of fuel consumed
#    n_years_sim=20 #Number of years for the simulation
#    Investment=130000 #Initial investment in €
#    OM_cost_year=5000 #Cost of O&M/year in €
    
    #SIMULATION
    #Variable initiation
    fuelPrizeArray=np.zeros(n_years_sim)
    Energy_produced=np.zeros(n_years_sim)
    Energy_savings=np.zeros(n_years_sim)
    BenefitESCO=np.zeros(n_years_sim)
    OM_cost=np.zeros(n_years_sim)
    Net_anual_savings=np.zeros(n_years_sim)
    Accumulated_savings=np.zeros(n_years_sim)
    FCF=np.zeros(n_years_sim)
    Acum_FCF=np.zeros(n_years_sim)
    
    for i in range(0,n_years_sim):
        if i==0:
            Energy_produced[i]=0
            Energy_savings[i]=0
            OM_cost[i]=0
            Net_anual_savings[i]=0
            Accumulated_savings[i]=0
            Acum_FCF[i]=0 #There is no investment
            FCF[i]=0
            fuelPrizeArray[i]=Fuel_price
        else:
            Energy_produced[i]=Energy_anual
            BenefitESCO[i]=priceReduction*(Energy_anual*(Fuel_price*(1+incremento*(i-1)))/Boiler_eff) #€ benefit for the ESCO
            Energy_savings[i]=(1-priceReduction)*(Energy_anual*(Fuel_price*(1+incremento*(i-1)))/Boiler_eff) + Co2_savings #€ benefit for the industry           
            OM_cost[i]=OM_cost_year
            Net_anual_savings[i]=BenefitESCO[i]-OM_cost[i]
            Accumulated_savings[i]=Accumulated_savings[i-1]+Net_anual_savings[i]
            Acum_FCF[i]=Acum_FCF[i-1]+Net_anual_savings[i]
            FCF[i]=Net_anual_savings[i]
            fuelPrizeArray[i]=(Fuel_price*(1+incremento*(i-1)))

    IRR10=100*np.irr(FCF[:10])
    IRR=100*np.irr(FCF)
    Amort_year=(Acum_FCF <= 0).sum()
    return [IRR,IRR10,Amort_year,Acum_FCF,FCF,BenefitESCO,OM_cost,fuelPrizeArray,Energy_savings,Net_anual_savings]