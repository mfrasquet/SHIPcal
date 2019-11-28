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
import glob
from matplotlib import pyplot as plt
import pandas as pd

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

"""



#filename="T3Hospitality.csv"
totalConsumption=3000000  #kWh
# --------------------------------DAY CONSUMPTION
#dayArray=[1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24]
#dayArray=[0.0400,0.0464,0.0480,0.0480,0.0480,0.0520,0.0560,0.0650,0.0840,0.0654,0.0456,0.0340,0.0260,0.0180,0.0180,0.0190,0.0240,0.0280,0.0374,0.0452	,0.0470,0.0374,0.0336,0.0340]
dayArray=[0,0,0,0,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,0,0] 
# --------------------------------WEEK CONSUMPTION
#weekArray=[1/7,1/7,1/7,1/7,1/7,1/7,1/7] #Constante
#weekArray=[0.120,0.120,0.120,0.120,0.120,0.200,0.200]
weekArray=[1/6,1/6,1/6,1/6,1/6,1/6,0] #Sin un día
# --------------------------------ANNUAL CONSUMPTION
monthArray=[1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12]
#monthArray=[0.1889825,0.1380204,0.1184213,0.0627570,0.0532994,0.0367279,0.0303713,0.0260941,0.0386296,0.0487369,0.1126647,0.1452948]

#annualHourly=demandCreator(totalConsumption,dayArray,weekArray,monthArray)
#print(annualHourly)
#print(len(annualHourly))
#print(sum(annualHourly))
#print(type(annualHourly))
#print(totalConsumption)


#
#fig = plt.figure()
#fig.suptitle('Anual', fontsize=14, fontweight='bold')
#ax1 = fig.add_subplot(111)  
#ax1 .plot(np.arange(8760), annualHourly,'.r-',label="Solar rad.")
#plt.tight_layout()
#
#fig = plt.figure()
#fig.suptitle('Semanal', fontsize=14, fontweight='bold')
#ax1 = fig.add_subplot(111)  
#ax1 .plot(np.arange(168), annualHourly[0:168],'.r-',label="Solar rad.")
#plt.tight_layout()
#
#fig = plt.figure()
#fig.suptitle('diario', fontsize=14, fontweight='bold')
#ax1 = fig.add_subplot(111)  
#ax1 .plot(np.arange(24), annualHourly[0:24],'.r-',label="Solar rad.")
#plt.tight_layout()
#
#print("Suma de los coef del vector diario "+str(100*sum(dayArray))+"%")
#print("Suma de los coef del vector semanal "+str(100*sum(weekArray))+"%")
#print("Suma de los coef del vector semanal "+str(100*sum(monthArray))+"%")
#print("Consumo anual perfil real: "+str(totalConsumption)+" kWh ")
#print("Consumo anual perfil simulado: "+str(int(sum(annualHourly)))+" kWh  Dif:"+str(100*round(sum(annualHourly)/totalConsumption,2))+"%")
#
#files_present = glob.glob(filename)
#if not files_present:
#    pd.DataFrame(annualHourly).to_csv(filename, sep=',',encoding = "utf-8",header=False,index=False)
#
#else:
#    print ('WARNING: This file already exists!')

"""