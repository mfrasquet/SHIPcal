# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 14:42:19 2017

Funcion para crear un consumo horario anual con 4 inputs:
- Consumo total anual
- Array de porcentajes dia
- Array de porcentajes semana
- Array de porcentajes mes
@author: miguel

"""
import numpy as np

# -------------------------------------------------------------------------
# -------------------------------  CONSOLE  -------------------------------
# -------------------------------------------------------------------------



def demandCreator(totalConsumption,dayArray,weekArray,monthArray):
    days_in_the_month=[31,28,31,30,31,30,31,31,30,31,30,31] #days_in_the_month[month_number]=how many days are in the month number "month_number"
    
    start_week_day=0 #Asume the first day starts in monday. I could make it variable with the datetime python module but I dont know the conequences in a server
    
    weight_of_hours_in_month=[] #Create the auxiliar list where I'll store the porcentage(weight) of use of every hour for the current month in the loop
    weight_of_hours_in_year=[] #Create the auxiliar list where I'll store the porcentage(weight) of use of every hour of one year
    
    for month_number in range(12): #For each month (12) in the year
        for day_of_the_month in range(days_in_the_month[month_number]): #Calculates the porcentage of use every hour for the whole month
            day=(start_week_day+day_of_the_month)%7 #Calculate wich day it is (Mon=0,Tues=1, ...) using the module 7, so day is which day in the week correspond to each day number in the month
            weight_of_hours_in_month += np.multiply(weekArray[day],dayArray).tolist() #Builts the array of use of every hour in the month, multiplying the porcentage of use of that specific day to the porcentage of use of each hour and then appends it to the end of the list (".tolist() method used to append as a list and do not sum as an array) as the next day.
        start_week_day=(day+1)%7 #pulls out which was the last day in the previus month to use it in the next day in the beginning of the next month
        weight_of_hours_in_year += np.multiply(monthArray[month_number],weight_of_hours_in_month).tolist() #Multiplies the hours of use of the month to the porcentage of use of the month in the year, then appends the list to the end of the weight_of_hours_in_year list
        weight_of_hours_in_month=[] #Restarts the weight_of_hours_in_month list to be used again for the next month data
       
    renormalization_factor=sum(weight_of_hours_in_year) #calculates the renormalization factor of the list in order to get "1" when summing all the 8760 elements.
    totalConsumption_normailized=totalConsumption/renormalization_factor #Renormalices the totalConsumption
    
    annualHourly=np.multiply(totalConsumption_normailized,weight_of_hours_in_year) #Obtains the energy required for every hour in the year.
        
    return (annualHourly)

# totalConsumption=1110521
# dayArray=[0.0009,0.0000,0.0000,0.0030,0.0083,0.0336,0.0692,0.0838,0.0776,0.0652,0.0686,0.0775,0.0774,0.0641,0.0602,0.0581,0.0541,0.0354,0.0400,0.0422,0.0431,0.0312,0.0040,0.0024]
# weekArray=[1/7,1/7,1/7,1/7,1/7,1/7,1/7]
# monthArray=[0.0468410773,0.03631628758,0.0803748871,0.0803748871,0.0803748871,0.09778113156,0.1127425776,0.1302037512,0.1238121566,0.1098808577,0.0572875254,0.0440099737]
# annualHourly=demandCreator(totalConsumption,dayArray,weekArray,monthArray)