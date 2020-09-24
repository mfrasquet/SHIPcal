#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 19:54:51 2016

Version record:
    - (1.1.1) Significant change in IAM function to allow Pitch/Azimuth/Roll
    - (1.1.5) OperationOilSimple included
    - (1.1.8) 5/1/2019 Modify code to allow offline simulations with other collectors,
    a very simple cost model has been included, this simplistic model will change
    in future versions, thanks to Jose Escamilla for his comments.
    - (1.1.9) 26/6/2019 Included savings Graph. Corrected savingsFraction = solarNetFraction. 
    Included boiler_eff for tacking care of energy before boiler (Energy_Before), which is different
    to energy after the boiler (Demand)
    - (1.1.10) 9/9/2019 New finance functions
       - (28/11/2019) Rebranding to SHIPcal to avoid confusion with solatom's propetary front-end ressspi  
       
@authors (in order of involvement): 
    Miguel Frasquet Herraiz - US/SOLATOM (mfrasquetherraiz@gmail.com)
    Joey Bannenberg - FONTYS UNIVERSITY (jhabannenberg@gmail.com)
    Yago NEl Vila Gracia - ETH (yagonelvilagracia@hotmail.com)
    Juan Antonio Aramburo Pasapera  - CIMAV (ja.arpa97@gmail.com)
"""

#Standard Libs
import sys
import os
import numpy as np
import pandas as pd
from iapws import IAPWS97

#Place to import SHIPcal Libs

from General_modules.func_General import DemandData,waterFromGrid_trim,thermalOil,reportOutputOffline, moltenSalt,waterFromGrid_v3 
from General_modules.demandCreator_v1 import demandCreator
from General_modules.fromDjangotoSHIPcal import djangoReport
from Solar_modules.EQSolares import SolarData
from Solar_modules.EQSolares import theta_IAMs
from Solar_modules.EQSolares import IAM_calc
from Finance_modules.FinanceModels import SP_plant_costFunctions
from Integration_modules.integrations import offStorageSimple, operationSimple, operationDSG, outputOnlyStorageSimple, outputWithoutStorageSimple, outputStorageSimple, offSimple,outputFlowsHTF,outputFlowsWater,operationDSG_Rec,offDSG_Rec,outputDSG_Rec # offOnlyStorageSimple, operationOnlyStorageSimple,
from Plot_modules.plottingSHIPcal import SankeyPlot, mollierPlotST, mollierPlotSH, thetaAnglesPlot, IAMAnglesPlot, demandVsRadiation, rhoTempPlotSalt, rhoTempPlotOil, viscTempPlotSalt, viscTempPlotOil, flowRatesPlot, prodWinterPlot, prodSummerPlot, productionSolar, storageWinter, storageSummer, storageNonAnnual, financePlot, prodMonths, savingsMonths,SL_S_PDR_Plot,storageNonAnnualSL_S_PDR

from Plot_modules.plottingSHIPcal_2 import demandVsRadiation2,thetaAnglesPlot2,IAMAnglesPlot2,flowRatesPlot2,prodWinterPlot2,prodSummerPlot2,productionSolar2,storageWinter2,storageSummer2,storageNonAnnual2,storageNonAnnualSL_S_PDR2,savingsMonths2,SL_S_PDR_Plot2,prodMonths2
from Solar_modules.EQSolares2 import SolarData3
from Integration_modules.integrations2 import operationSimple2, operationDSG2, operationDSG_Rec2
from General_modules.djangotoSHIPCal2 import djangoReport2




def demandCreator2(totalConsumption,dayArray,weekArray,monthArray,step_minArray,itercontrol):
    days_in_the_month=[31,28,31,30,31,30,31,31,30,31,30,31] #days_in_the_month[month_number]=how many days are in the month number "month_number"
    
    start_week_day=0 #Asume the first day starts in monday. I could make it variable with the datetime python module but I dont know the conequences in a server
    
    if itercontrol=='paso_10min':
    
        weight_of_ten_min_in_day=[]
        weight_of_ten_min_in_month=[]
        weight_of_ten_min_in_year=[]
        
        for month_number in range(12): #For each month (12) in the year
            for day_of_the_month in range(days_in_the_month[month_number]): #Calculates the porcentage of use every hour for the whole month
                day=(start_week_day+day_of_the_month)%7 #Calculate wich day it is (Mon=0,Tues=1, ...) using the module 7, so day is which day in the week correspond to each day number in the month
                for hour in range(len(dayArray)):
                    weight_of_ten_min_in_day += np.multiply(dayArray[hour],step_minArray).tolist()
            
            
                weight_of_ten_min_in_month += np.multiply(weekArray[day], weight_of_ten_min_in_day).tolist()
                weight_of_ten_min_in_day=[]
            start_week_day=(day+1)%7 #pulls out which was the last day in the previus month to use it in the next day in the beginning of the next month
            weight_of_ten_min_in_year += np.multiply(monthArray[month_number],weight_of_ten_min_in_month).tolist()
            weight_of_ten_min_in_month=[]
        
       
        
        renormalization_factor=sum( weight_of_ten_min_in_year) #calculates the renormalization factor of the list in order to get "1" when summing all the 8760 elements.
        totalConsumption_normailized=totalConsumption/renormalization_factor #Renormalices the totalConsumption
    
    
        annual=np.multiply(totalConsumption_normailized,weight_of_ten_min_in_year)
    
    elif itercontrol=='paso_15min':
        
        weight_of_fifteen_min_in_day=[]
        weight_of_fifteen_min_in_month=[]
        weight_of_fifteen_min_in_year=[]
       
        for month_number in range(12): #For each month (12) in the year
            for day_of_the_month in range(days_in_the_month[month_number]): #Calculates the porcentage of use every hour for the whole month
                day=(start_week_day+day_of_the_month)%7 #Calculate wich day it is (Mon=0,Tues=1, ...) using the module 7, so day is which day in the week correspond to each day number in the month
                for hour in range(len(dayArray)):
                    weight_of_fifteen_min_in_day += np.multiply(dayArray[hour],step_minArray).tolist()
            
            
                weight_of_fifteen_min_in_month += np.multiply(weekArray[day], weight_of_fifteen_min_in_day).tolist()
                weight_of_fifteen_min_in_day=[]
            start_week_day=(day+1)%7 #pulls out which was the last day in the previus month to use it in the next day in the beginning of the next month
            weight_of_fifteen_min_in_year += np.multiply(monthArray[month_number],weight_of_fifteen_min_in_month).tolist()
            weight_of_fifteen_min_in_month=[]
       
       
        
        renormalization_factor=sum( weight_of_fifteen_min_in_year) #calculates the renormalization factor of the list in order to get "1" when summing all the 8760 elements.
        totalConsumption_normailized=totalConsumption/renormalization_factor #Renormalices the totalConsumption
    
    
        annual=np.multiply(totalConsumption_normailized,weight_of_fifteen_min_in_year)
   
    return (annual)


def calc_min_year(mes,dia,hora,minute,itercontrol):
    mes_string=("Ene","Feb","Mar","Apr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dec") #Not in use!!! remove
    mes_days=(31,28,31,30,31,30,31,31,30,31,30,31)
    
    num_days=0 #Initializate the variables
    cont_mes=mes-1
    if mes<=12: #Check that the month input is reliable
        while (cont_mes >0):
            cont_mes=cont_mes-1 #Counts backwards from the introduced month to the first month in the year(January)
        
            num_days=num_days+mes_days[cont_mes] #Adds all the days in the months previous to the introduced one
            
            
        if dia<=mes_days[mes-1]: #Checks that the introduced dau number is smaller than the number of days in that month
            num_days=num_days+dia #Adds the quantity of days passed so far in the introduced month
        else:
            raise ValueError('Day should be <=days_month')    
    else:
        raise ValueError('Month should be <=12')
    
  
    if hora<=24: #Checks that the hour number is less than 24
       hour_year=(num_days-1)*24+hora #Calculates the current year hour
    else:
       
        raise ValueError('Hour should be <=24') 
   
    if itercontrol=='paso_10min':
    
        if minute<=5 and minute>=0:
        
            min_year=hour_year*6+minute+1
        else:
             raise ValueError('Ten_min has to be 0, 1, 2, 3, 4 or 5')
    elif itercontrol=='paso_15min':
        
        if  minute<=3 and minute>=0:
            
            min_year=hour_year*4+minute+1
        
        else :
            raise ValueError('Fifteen_min has to be 0, 1, 2 or 3')
    return min_year
        
    


def DemandData2(file_demand,mes_ini_sim,dia_ini_sim,hora_ini_sim,mes_fin_sim,dia_fin_sim,hora_fin_sim, min_ini_sim, min_fin_sim, itercontrol):
    
#    Demand = np.loadtxt(file_demand, delimiter=",")
    Demand=np.array(file_demand)
    

    min_year_ini=calc_min_year(mes_ini_sim,dia_ini_sim,hora_ini_sim, min_ini_sim, itercontrol)
    min_year_fin=calc_min_year(mes_fin_sim,dia_fin_sim,hora_fin_sim, min_fin_sim, itercontrol)
    
    
  
    if min_year_ini <= min_year_fin:
        sim_steps=min_year_fin-min_year_ini
    
    else:
        raise ValueError('End time is smaller than start time') 


    #Bucle de simulacion
    Demand_sim=np.zeros (sim_steps)
    step_sim=np.zeros (sim_steps)
    
    
    step=0
    for step in range(0,sim_steps):
        step_sim[step]=step
       
        Demand_sim[step]=Demand[min_year_ini+step-1]
        step+=1
        

    
    return Demand_sim







def SolarEQ_simple3 (to_solartime,long,huso,Month,Day,Hour,Lat,Huso): #Returns the hour angle (W) [rad], sun elevation angle[rad], azimuth angle[rad], declination [rad] and zenithal angle [rad] of the sun for each the specified hour, latitude[°], anf time zone given in the inputs.

    gr=np.pi/180; #Just to convert RAD-DEG 
    
    #Read the Juilan day file and save it in a matrix
    "JUL_DAY=np.loadtxt(os.path.dirname(os.path.dirname(__file__))+'/Solar_modules/Julian_day_prueba.txt',delimiter='\t');"
    JUL_DAY=np.loadtxt(os.path.dirname(__file__)+'/Solar_modules/Julian_day_prueba.txt',delimiter='\t');
  
    
    #Calculates the Julian Day
    Jul_day=JUL_DAY[int(Day-1),int(Month-1)];
    
    #Declination
    
    DJ=2*np.pi/365*(Jul_day-1); #Julian day in rad
    DECL=(0.006918-0.399912*np.cos(DJ)+ 0.070257*np.sin(DJ)-0.006758*np.cos(2*DJ)+0.000907*np.sin(2*DJ)-0.002697*np.cos(3*DJ)+0.00148*np.sin(3*DJ));
    DECL_deg=DECL/gr;
    
    if to_solartime=='on': #Calculates solar time.
         
        num_days=calc_day_year(int(Month),int(Day))
        B=(360/365)*(num_days-81)
        LSTM=15*huso
        EOT=9.87*np.sin(2*B)-7.53*np.cos(B)-1.5*np.sin(B)
        tc=4*(long-LSTM)+EOT
        Hour=tc/60+Hour+ 3.5/60
    
    #Hour
    W_deg=(Hour-12)*15;
    W=W_deg*gr;
    
    #Sun elevation
    XLat=Lat*gr;
    sin_Elv=np.sin(DECL)*np.sin(XLat)+np.cos(DECL)*np.cos(XLat)*np.cos(W);
    SUN_ELV=np.arcsin(sin_Elv);
    SUN_ELV_deg=SUN_ELV/gr;
    
    SUN_ZEN=(np.pi/2)-SUN_ELV;
    #Sun azimuth
    SUN_AZ=np.arcsin(np.cos(DECL)*np.sin(W)/np.cos(SUN_ELV));
    
    verif=(np.tan(DECL)/np.tan(XLat));
    if np.cos(W)>=verif:
        SUN_AZ=SUN_AZ;  
    else:
            if SUN_AZ >0:
                SUN_AZ=((np.pi/2)+((np.pi/2)-abs(SUN_AZ)));
            else:
                SUN_AZ=-((np.pi/2)+((np.pi/2)-abs(SUN_AZ)));
    
    
    
#    SUN_AZ_deg=SUN_AZ/gr;
#    a=[W,SUN_ELV,SUN_AZ,DECL,SUN_ZEN]
       
    return [W,SUN_ELV,SUN_AZ,DECL,SUN_ZEN]




def SolarData2(file_loc,mes_ini_sim,dia_ini_sim,hora_ini_sim,min_ini_sim,mes_fin_sim,dia_fin_sim,hora_fin_sim,min_fin_sim, itercontrol,huso,to_solartime ,long,sender='notCIMAV',Lat=0,Huso=0, optic_type='0'): #This function returns an "output" array with the month, day of the month, hour of the day, hour of the year hour angle,SUN_ELVevation, suN_AZimuth,DECLINATION, SUN_ZENITHAL, DNI,temp_sim,step_sim for every hour between the starting and ending hours in the year.  It also returns the starting and ending hour in the year.


    
    min_year_ini=calc_min_year(mes_ini_sim,dia_ini_sim,hora_ini_sim, min_ini_sim, itercontrol)
    min_year_fin=calc_min_year(mes_fin_sim,dia_fin_sim,hora_fin_sim, min_fin_sim, itercontrol)
    
    
    if min_year_ini <= min_year_fin: #Checks that the starting time is before than the ending time
        sim_steps=min_year_fin-min_year_ini #Stablishes the number of steps as the hours between the starting and ending hours
    else:
        raise ValueError('End time is smaller than start time') 
    
    
    #Llamada al archivo de meteo completo
    if sender == 'CIMAV':
        Lat,Huso,Positional_longitude,data,DNI,temp=Meteo_data(file_loc,sender,optic_type)
    elif sender == 'SHIPcal':
        from simforms.models import Locations, MeteoData
        data = MeteoData.objects.filter(location=Locations.objects.get(pk=file_loc)).order_by('hour_year_sim')
        temp = data.values_list('temp',flat=True)
        if optic_type=='concentrator' or optic_type=='0':
            DNI = data.values_list('DNI',flat=True)
        else:
            DNI = data.values_list('GHI',flat=True)#DNI actually carries the GHI information
    else:
        (data,DNI,temp)=Meteo_data2(file_loc,sender)#Calls another function within this same script that reads the TMY.dat file 
        #They are already np.arrays
        #data=np.array(data) #Array where every row is an hour and the columns are month,day in the month, hour of the month, hour of the year, ..., DNI, Temp
        #DNI=np.array(DNI) #Vector with DNI values for every hour in the year
        #temp=np.array(temp) #Vector with the temperature for every hour in the year
    
    #Bucle de simulacion
    #Starts the vectors of sim_steps length to store data in them
    
    W_sim=np.zeros (sim_steps)
    SUN_ELV_sim=np.zeros (sim_steps)
    SUN_AZ_sim=np.zeros (sim_steps)
    DECL_sim=np.zeros (sim_steps)
    SUN_ZEN_sim=np.zeros (sim_steps)
    
    #The file was already readed, and the data was already stored in "data" so it is easier to just pick the needed sections.
    step_sim=np.array(range(0,sim_steps)) #np.zeros (sim_steps)
    DNI_sim=np.array(DNI[min_year_ini-1: min_year_fin-1])
    temp_sim=np.array(temp[min_year_ini-1: min_year_fin-1])
    if sender=='SHIPcal':
        month_sim=np.array(data.values_list('month_sim',flat=True)[min_year_ini-1:min_year_fin-1])
        day_sim=np.array(data.values_list('day_sim',flat=True)[min_year_ini-1:min_year_fin-1])
        hour_sim=np.array(data.values_list('hour_sim',flat=True)[min_year_ini-1:min_year_fin-1])
        min_sim=np.array(data.values_list('min_sim',flat=True)[min_year_ini-1:min_year_fin-1])
        min_year_sim=np.array(data.values_list('hour_year_sim',flat=True)[min_year_ini-1:min_year_fin-1])
    else:
        month_sim=data[min_year_ini-1:min_year_fin-1,0]
        day_sim=data[min_year_ini-1:min_year_fin-1,1]
        hour_sim=data[min_year_ini-1:min_year_fin-1,2]
        min_sim=data[min_year_ini-1:min_year_fin-1,3]
        min_year_sim=data[min_year_ini-1:min_year_fin-1,4]
    
    
    step=0
    for step in range(0,sim_steps):
        #Posicion solar
        W,SUN_ELV,SUN_AZ,DECL,SUN_ZEN=SolarEQ_simple2 (month_sim[step],day_sim[step] ,hour_sim[step], min_sim[step],huso,to_solartime,long,Lat,Huso) #calls another function in within this script that calculates the solar positional angles for the specfied hour of the day and month
        W_sim[step]=W
        SUN_ELV_sim[step]=SUN_ELV   #rad
        SUN_AZ_sim[step]=SUN_AZ     #rad
        DECL_sim[step]=DECL         #rad
        SUN_ZEN_sim[step]=SUN_ZEN   #rad
     
        
        step+=1
    
    output=np.column_stack((month_sim,day_sim,hour_sim,min_sim,min_year_sim,W_sim,SUN_ELV_sim,SUN_AZ_sim,DECL_sim,SUN_ZEN_sim,DNI_sim,temp_sim,step_sim)) #Arranges the calculated data in a massive array with the previusly calculated vector as columns
    
    """
    Output key:
    output[0]->month of year
    output[1]->day of month
    output[2]->hour of day
    output[3]-> minutes portions of hour
    output[4]-> minutes portions of the year
    output[5]->W - rad
    output[6]->SUN_ELV - rad
    output[7]->SUN AZ - rad
    output[8]->DECL - rad
    output[9]->SUN ZEN - rad
    output[10]->DNI  - W/m2
    output[11]->temp -C
    output[12]->step_sim
    """
        

    
    if sender == 'CIMAV':
        return Lat,Huso,Positional_longitude,output
    else:
        return[output,min_year_ini,min_year_fin] 



def Meteo_data2 (file_meteo,sender='notCIMAV', optic_type='0'): #This function exports the TMY file to 'data', the DNI and temperature array of values for  each step in the year from the file_meteo path to file
    #Only if the optional argument sender is received and is == 'CIMAV'
     #Only diference with Meteo_Data is data´s rows for DNI and temp are 9 and 10 instead 8 and 9.
    
    if sender == 'CIMAV':
        data = np.loadtxt(file_meteo, delimiter="\t", skiprows=4) #Will read this format, since the first 4 rows has the place, location and headings data
        if optic_type=='concentrator':
            DNI=data[:,5]#If the collector is a concentrator type collector this variable will carry the DNI
        else:
            DNI=data[:,6]#But if it is not a concentrator type it will carry the global radiation
        temp=data[:,7]
        f=open(file_meteo,'r') #Opens the selected file
        for i, line in enumerate(f): #Starts reading line by line and assign a line number to each as it is reads the line (starts from 0)
            if i==1: #When the unctions reads line 2, which is where the Lat and time Zone is
                position=line #Stores the information in the position variable as a string
            if i>2: #It doesn't read the following lines since it already has the required information
                break #So it stops
        f.close() #Close the file
        position=position.split() #Converts the string to a list of strings [Lat,Long,Altitude,TimeZone(Huso)]
        position=[float(i) for i in position] #Converts each of the items into a float number
        Lat=position[0] #Stores the Lat and the TimeZone in variables for later return
        Positional_longitude=position[1]
        Huso=position[3]
        return Lat,Huso,Positional_longitude,data,DNI,temp #Returns the Lat and Time zone corresponding variables
    else:
        data = np.loadtxt(file_meteo, delimiter="\t")
        DNI=data[:,9]
        temp=data[:,10]
        return [data,DNI,temp]




def SolarEQ_simple2 (Month,Day,Hour,minute,huso,to_solartime,long,Lat,Huso): #Returns the hour angle (W) [rad], sun elevation angle[rad], azimuth angle[rad], declination [rad] and zenithal angle [rad] of the sun for each the specified hour, latitude[°], anf time zone given in the inputs.

    gr=np.pi/180; #Just to convert RAD-DEG 
    
    #Read the Juilan day file and save it in a matrix
    "JUL_DAY=np.loadtxt(os.path.dirname(os.path.dirname(__file__))+'/Solar_modules/Julian_day_prueba.txt',delimiter='\t');"
    JUL_DAY=np.loadtxt(os.path.dirname(__file__)+'/Solar_modules/Julian_day_prueba.txt',delimiter='\t');
    
    #Calculates the Julian Day
    Jul_day=JUL_DAY[int(Day-1),int(Month-1)];
    
    #Declination
    
    DJ=2*np.pi/365*(Jul_day-1); #Julian day in rad
    DECL=(0.006918-0.399912*np.cos(DJ)+ 0.070257*np.sin(DJ)-0.006758*np.cos(2*DJ)+0.000907*np.sin(2*DJ)-0.002697*np.cos(3*DJ)+0.00148*np.sin(3*DJ));
    DECL_deg=DECL/gr;
    
    
    #Hour
    
    if to_solartime=='on': #Calculates solar time.
         
        num_days=calc_day_year(int(Month),int(Day))
        B=(360/365)*(num_days-81)
        LSTM=15*huso
        EOT=9.87*np.sin(2*B)-7.53*np.cos(B)-1.5*np.sin(B)
        tc=4*(long-LSTM)+EOT
        Hour=tc/60+Hour+((minute)/60)+ 3.5/60
    
        if Hour==0:
            W_deg=-1*(Hour-12)*15;
            W=W_deg*gr;
        else:
            W_deg=(Hour-12)*15;
            W=W_deg*gr;
    else:
        if Hour==0:
            W_deg=-1*(Hour+(minute/60)-12)*15;
            W=W_deg*gr;
        else:
            W_deg=(Hour+(minute/60)-12)*15;
            W=W_deg*gr;
   
    
    #Sun elevation
    XLat=Lat*gr;
    sin_Elv=np.sin(DECL)*np.sin(XLat)+np.cos(DECL)*np.cos(XLat)*np.cos(W);
    SUN_ELV=np.arcsin(sin_Elv);
    SUN_ELV_deg=SUN_ELV/gr;
    
    SUN_ZEN=(np.pi/2)-SUN_ELV;
    #Sun azimuth
    SUN_AZ=np.arcsin(np.cos(DECL)*np.sin(W)/np.cos(SUN_ELV));
    
    verif=(np.tan(DECL)/np.tan(XLat));
    if np.cos(W)>=verif:
        SUN_AZ=SUN_AZ;  
    else:
            if SUN_AZ >0:
                SUN_AZ=((np.pi/2)+((np.pi/2)-abs(SUN_AZ)));
            else:
                SUN_AZ=-((np.pi/2)+((np.pi/2)-abs(SUN_AZ)));
    
    
    
#    SUN_AZ_deg=SUN_AZ/gr;
#    a=[W,SUN_ELV,SUN_AZ,DECL,SUN_ZEN]
       
    return [W,SUN_ELV,SUN_AZ,DECL,SUN_ZEN]

def calc_day_year(mes,dia):
    
    mes_days=(31,28,31,30,31,30,31,31,30,31,30,31)
    
    num_days=0 #Initializate the variables
    cont_mes=mes-1
    if mes<=12: #Check that the month input is reliable
        while (cont_mes >0):
            cont_mes=cont_mes-1 #Counts backwards from the introduced month to the first month in the year(January)
        
            num_days=num_days+mes_days[cont_mes] #Adds all the days in the months previous to the introduced one
            
            
        if dia<=mes_days[mes-1]: #Checks that the introduced dau number is smaller than the number of days in that month
            num_days=num_days+dia #Adds the quantity of days passed so far in the introduced month
        else:
            raise ValueError('Day should be <=days_month')    
    else:
        raise ValueError('Month should be <=12')
        
    return (num_days)



def waterFromGrid_v3_min(file_meteo, itercontrol, sender='CIMAV'):
    if sender=='CIMAV':
        Tamb = np.loadtxt(file_meteo, delimiter="\t", skiprows=4)[:,7]#Reads the temperature of the weather. The TMYs are a bit different.
    elif sender=='SHIPcal':
        from simforms.models import Locations, MeteoData
        meteo_data = MeteoData.objects.filter(location=Locations.objects.get(pk=file_meteo))
        Tamb = meteo_data.order_by('hour_year_sim').values_list('temp',flat=True)
    else:
        Tamb = np.loadtxt(file_meteo, delimiter="\t")[:,10]#Reads the temperature of the weather
    TambAverage=np.mean(Tamb) #Computes the year average
    TambMax=np.amax(Tamb) #Computes the maximum temperature
    
    offset = 3 #A defined offset of 3 °C
    ratio = 0.22 + 0.0056*(TambAverage - 6.67)
    lag = 1.67 - 0.56*(TambAverage - 6.67)
#The offset, lag, and ratio values were obtained by fitting data compiled by Abrams and Shedd [8], the FloridaSolar Energy Center [9], and Sandia National Labs
    
    T_in_C_AR=[] #It is easier to work with this array as a list first to print 24 times the mean value of the water temperature for every day
    
    if itercontrol=='paso_10min':
        for day in range(365):
            #The ten-minute year array is built by the temperature calculated for the day printed 144 times for each day
            T_in_C_AR+=[(TambAverage+offset)+ratio*(TambMax/2)*np.sin(np.radians(-90+(day-15-lag)*360/365))]*24*6 #This was taken from TRNSYS documentation.
    elif itercontrol=='paso_15min':
        for day in range(365):
            #The fifteen-minute year array is built by the temperature calculated for the day printed 96 times for each day
            T_in_C_AR+=[(TambAverage+offset)+ratio*(TambMax/2)*np.sin(np.radians(-90+(day-15-lag)*360/365))]*24*4
    return np.array(T_in_C_AR)





def waterFromGrid_trim2(T_in_C_AR,mes_ini_sim,dia_ini_sim,hora_ini_sim,mes_fin_sim,dia_fin_sim,hora_fin_sim,min_ini_sim,min_fin_sim):
    
    min_year_ini=calc_min_year(mes_ini_sim,dia_ini_sim,hora_ini_sim, min_ini_sim,itercontrol)
    min_year_fin=calc_min_year(mes_fin_sim,dia_fin_sim,hora_fin_sim, min_fin_sim, itercontrol)
    
    if min_year_ini <= min_year_fin: #Checks that the starting time is before than the ending time
        sim_steps=min_year_fin-min_year_ini #Stablishes the number of steps as.
    else:
        raise ValueError('End time is smaller than start time')   
    
    T_in_C_AR_trim=np.zeros (sim_steps)
    
    step=0
    for step in range(0,sim_steps):
        T_in_C_AR_trim[step]=T_in_C_AR[min_year_ini+step-1]
        step+=1
    
    return (T_in_C_AR_trim) 



#PLOTS MODIFICATIONS--->only x label but I cannot modify functions files so i have to copy all the functions here.





def SHIPcal(origin,inputsDjango,plots,imageQlty,confReport,modificators,desginDict,simControl,pk):
    
#%%
# ------------------------------------------------------------------------------------
# BLOCK 1 - VARIABLE INITIALIZATION --------------------------------------------------
# ------------------------------------------------------------------------------------
    
    # BLOCK 1.1 - SIMULATION CONTROL <><><><><><><><><><><><><><><><><><><><><><><><><><><>
    
    version="1.1.10" #SHIPcal version
    lang=confReport['lang'] #Language
    sender=confReport['sender'] #Sender identity. Needed for use customized modules or generic modules (Solar collectors, finance, etc.)

    
    #-->  Paths
    if sender=='solatom': #The request comes from Solatom's front-end www.ressspi.com
        sys.path.append(os.path.dirname(os.path.dirname(__file__))+'/ressspi_solatom/') #SOLATOM
    
    elif sender=='CIMAV': #The request comes from CIMAV front-end
        sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/CIMAV/') #CIMAV collectors information databases and TMYs

    if origin==-2: #Simulation called from ReSSSPI front-end
        plotPath=os.path.dirname(os.path.dirname(__file__))+'/ressspi/ressspiForm/static/results/' #FilePath for images when called by www.ressspi.com
    elif origin==-3:
        plotPath=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/CIMAV/results' #FilePath for images when called cimav
    elif origin==0:
        plotPath=""
    elif origin==1: #Simulation called from other front-ends (use positive integers)
        plotPath=""
        
    #-->  Propetary libs
    if sender=='solatom': #The request comes from Solatom's front-end www.ressspi.com
        from Solatom_modules.solatom_param import optic_efficiency_N
        from Solatom_modules.solatom_param import solatom_param
        from Solatom_modules.Solatom_finance import SOL_plant_costFunctions
        from Solatom_modules.templateSolatom import reportOutput
        from Finance_modules.FinanceModels import Turn_key, ESCO
    elif sender=='CIMAV': #The request comes from CIMAV front-end
        from CIMAV.CIMAV_modules.fromDjangotoRessspivCIMAV import djangoReport as djangoReportCIMAV
        from CIMAV.meteorologic_database.meteoDBmanager import Lat_Huso
        from CIMAV.CIMAV_modules.CIMAV_collectors import CIMAV_collectors,IAM_fiteq,IAM_calculator #Imports a CIMAV's module to return the parameters of collectors supported by CIMAV
        from CIMAV.CIMAV_modules.incidence_angle import theta_IAMs_v2 as theta_IAMs_CIMAV
        from CIMAV.CIMAV_modules.CIMAV_financeModels import Turn_key,ESCO,CIMAV_plant_costFunctions
    else:
        from Finance_modules.FinanceModels import Turn_key, ESCO
    
    #-->  Simulation options
    finance_study=simControl['finance_study'] #In order to include the financial study. 1-> Yes ; 0-> No
    
    #-->  Simulation length
    
    # Initial step of the simulation
    month_ini_sim=simControl['mes_ini_sim']   # Month in which the simulation starts 
    day_ini_sim=simControl['dia_ini_sim']   # Day in which the simulation starts 
    hour_ini_sim=simControl['hora_ini_sim'] # Hour in which the simulation starts 
    
    # Final step of the simulation
    month_fin_sim=simControl['mes_fin_sim']   # Month in which the simulation ends
    day_fin_sim=simControl['dia_fin_sim']   # Day in which the simulation ends
    hour_fin_sim=simControl['hora_fin_sim'] # Hour in which the simulation ends
    
    if simControl['itercontrol']=='paso_10min':
        # Initial step of the simulation
        month_ini_sim=simControl['mes_ini_sim']   # Month in which the simulation starts 
        day_ini_sim=simControl['dia_ini_sim']   # Day in which the simulation starts 
        hour_ini_sim=simControl['hora_ini_sim'] # Hour in which the simulation starts 
        ten_min_ini_sim=simControl['ten_min_ini_sim'] #Step of 10 minutes in which the simulation starts
    
        # Final step of the simulation
        month_fin_sim=simControl['mes_fin_sim']   # Month in which the simulation ends
        day_fin_sim=simControl['dia_fin_sim']   # Day in which the simulation ends
        hour_fin_sim=simControl['hora_fin_sim'] # Hour in which the simulation ends                   
        ten_min_fin_sim=simControl['ten_min_fin_sim'] #Step of 10 minutes in which the simulations ends
    elif simControl['itercontrol']=='paso_15min':
        # Initial step of the simulation
        month_ini_sim=simControl['mes_ini_sim']   # Month in which the simulation starts 
        day_ini_sim=simControl['dia_ini_sim']   # Day in which the simulation starts 
        hour_ini_sim=simControl['hora_ini_sim'] # Hour in which the simulation starts
        fifteen_min_ini_sim=simControl['fifteen_min_ini_sim'] #Step of 15 minutes in which the simulations starts
    
        # Final step of the simulation
        month_fin_sim=simControl['mes_fin_sim']   # Month in which the simulation ends
        day_fin_sim=simControl['dia_fin_sim']   # Day in which the simulation ends
        hour_fin_sim=simControl['hora_fin_sim'] # Hour in which the simulation ends                   
        fifteen_min_fin_sim=simControl['fifteen_min_fin_sim'] #Step of 15 minutes in which the simulations ends
                                       
                                       
                                       
                                       
                                       
        
    #%%
    # BLOCK 1.2 - PARAMETERS <><><><><><><><><><><><><><><><><><><><><><><><><><><>
    
    #--> Finance parameters
    fuelCostRaise=3.5 # Annual increase of fuel price [%]
    
    # Annual increase of the price of money through Consumer Price Index [%]
    if sender == 'CIMAV':
        CPI=5 # 5 for México
        
        #Some specific fuels increase
        if inputsDjango['fuel'] == 'electricidad':
            fuelCostRaise=7.09 #[%] From thesis :“Análisis térmico de la envolvente de naves industriales con incorporación de tecnología solar fotovoltaica” by CARLOS ARMANDO ESPINO REYES May 2019
        elif inputsDjango['fuel'] == 'gas_natural':
            fuelCostRaise=11.47 #[%] From thesis :“Análisis térmico de la envolvente de naves industriales con incorporación de tecnología solar fotovoltaica” by CARLOS ARMANDO ESPINO REYES May 2019
        elif inputsDjango['fuel'] == 'diesel':
            fuelCostRaise=6.52 # [%] Information from http://www.intermodalmexico.com.mx/Portal/AjusteCombustible/Historico#
        elif inputsDjango['fuel'] == 'gasolina_nafta':
            fuelCostRaise=9.76 # [%] Information from https://datos.gob.mx/busca/dataset/ubicacion-de-gasolineras-y-precios-comerciales-de-gasolina-y-diesel-por-estacion
        elif inputsDjango['fuel'] == 'gas_licuado_petroleo':
            fuelCostRaise=3 #[%] Information from https://datos.gob.mx/busca/dataset/precios-maximos-de-venta-de-primera-mano-en-materia-de-gas-lp
        #elif fuel == 'coque_carbon':
            #fuelCostRaise= #[%] Information from
    else:
        CPI=2.5 # 2.5 for Spain 
        
    costRaise=CPI/100+fuelCostRaise/100
    priceReduction=10 #[%] NOT USED
    
    n_years_sim=25 # Collector life in years & number of years for the simulation [years]
    
    
    #--> Integration parameters
    
    lim_inf_DNI=200 # Minimum temperature to start production [W/m²]
    m_dot_min_kgs=0.1 # Minimum flowrate before re-circulation [kg/s]
    coef_flow_rec=1 # Multiplier for flowrate when recirculating [-]
    Boiler_eff=0.8 # Boiler efficiency to take into account the excess of fuel consumed [-]
    subcooling=5 #Deegre of subcooling
    
        ## SL_L_RF
    heatFactor=0.7 # Percentage of temperature variation (T_out - T_in) provided by the heat exchanger (for design) 
    HX_eff=0.9 # Simplification for HX efficiency
    DELTA_ST=30 # Temperature delta over the design process temp for the storage
    
    ## SL_L_S_PH & SL_L_RF
    DELTA_HX=5 # Degrees for temperature delta experienced in the heat exchanger (for design) 

#    flowrate_design_kgs=2 # Design flow rate (fix value for SL_L_S)
    
    
    #%%
    # BLOCK 1.3 - SYSTEM VARIABLES <><><><><><><><><><><><><><><><><><><><><><><><><><><>    
    
    #--> Simulation modifiers (useful to control extraordinary situations)
    mofINV=modificators['mofINV'] # Investment modificator to include: Subsidies, extra-costs, etc. [-]
    mofDNI=modificators['mofDNI'] # DNI modificator to take into correct Meteonorm data if necessary [-] 
    mofProd=modificators['mofProd'] # Production modificator to include: Dusty environments, shadows, etc. [-]
    
    
    # --> Solar field
    num_loops=desginDict['num_loops'] # Number of loops of the solar plant [-]
    n_coll_loop=desginDict['n_coll_loop'] # Number of modules connected in series per loop [-]
    
        ## --> Solar collector 
        
    if sender=='solatom': #Using Solatom Collector
        
        ## IAM 
        IAM_file='Solatom.csv'
        IAM_folder=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/IAM_files/"
        IAMfile_loc=IAM_folder+IAM_file
        
        ## Solar collector characteristics
        type_coll=20 #Solatom 20" fresnel collector - Change if other collector is used
        REC_type=1
        D,Area_coll,rho_optic_0,huella_coll,Long,Apert_coll=solatom_param(type_coll)

        coll_par = {'type_coll':type_coll,'REC_type':REC_type,'Area_coll':Area_coll,'rho_optic_0':rho_optic_0,'IAMfile_loc':IAMfile_loc,'Long':Long}
    
    elif sender=='CIMAV': #Use one of the collectors supported by CIMAV
        type_coll=inputsDjango['collector_type']#The collector datasheet will have this name
        Area_coll,rho_optic_0,eta1,eta2,mdot_test,Long,weight=CIMAV_collectors(type_coll) 
        IAM_file='defaultCollector.csv' #Se puede borrar despues 
        REC_type=1#Se puede borrar despues 
        IAM_folder=os.path.dirname(os.path.realpath(__file__))+"/Collector_modules/"
    
    else: #Using other concentrating collectors (to be filled with customized data)
        
        ## IAM 
        IAM_file='defaultCollector.csv'
        IAM_folder=os.path.dirname(__file__)+"/Collector_modules/"
        IAMfile_loc=IAM_folder+IAM_file
        
        ## Solar collector characteristics
        REC_type=1 #Type of receiver used (1 -> Schott receiver tube)
        Area_coll=26.4 #Aperture area of collector per module [m²]
        rho_optic_0=0.75583 #Optical eff. at incidence angle=0 [º]
        Long=5.28 #Longitude of each module [m]
        type_coll = 'default'
        coll_par = {'type_coll':type_coll,'REC_type':REC_type,'Area_coll':Area_coll,'rho_optic_0':rho_optic_0,'IAMfile_loc':IAMfile_loc,'Long':Long}
        
    Area=Area_coll*n_coll_loop #Area of aperture per loop [m²] Used later
    Area_total=Area*num_loops #Total area of aperture [m²] Used later
    num_modulos_tot=n_coll_loop*num_loops
    
        ## --> TO BE IMPLEMENTED Not used for the moment, it will change in future versions
    """    
    orientation="NS"
    inclination="flat" 
    shadowInput="free"
    terreno="clean_ground"
    """

    beta=0 #Pitch not implemented [rad]
    orient_az_rad=0 #Orientation not implemented [rad]
    roll=0 #Roll not implemented [rad]

    
    # --> Front-end inputs
    
    if origin==-2: #Simulation called from front-end -> www.ressspi.com
        
        #Retrieve front-end inputs
        [inputs,annualConsumptionkWh,P_op_bar,monthArray,weekArray,dayArray]=djangoReport(inputsDjango) 
        ## METEO
        meteoDB = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/meteoDB.csv", sep=',') #Reads the csv file where the register of the exiting TMY is.
        locationFromRessspi=inputs['location'] #Extracts which place was selected from the form 
        localMeteo=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'meteoFile'].iloc[0] #Selects the name of the TMY file that corresponds to the place selected in the form
        file_loc=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/"+localMeteo #Stablishes the path to the TMY file
        Lat=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'Latitud'].iloc[0] #Extracts the latitude from the meteoDB.csv file for the selected place
        Huso=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'Huso'].iloc[0] #Extracts the time zone for the selected place

        ## INTEGRATION
        type_integration=desginDict['type_integration'] # Type of integration scheme from IEA SHC Task 49 "Integration guidelines" http://task49.iea-shc.org/Data/Sites/7/150218_iea-task-49_d_b2_integration_guideline-final.pdf
        almVolumen=desginDict['almVolumen'] # Storage capacity [litres]
        
        ## INDUSTRIAL APPLICATION
            #>> PROCESS
        fluidInput=inputs['fluid'] #Type of fluid 
        T_process_in=inputs['outletTemp'] #HIGH - Process temperature [ºC]
        T_process_out=inputs['inletTemp'] #LOW - Temperature at the return of the process [ºC]
        P_op_bar=P_op_bar #[bar]
            
            #>> ENERGY DEMAND
        
        if inputs['location_aux']=="":
            file_demand=demandCreator(annualConsumptionkWh,dayArray,weekArray,monthArray)
        else:
            file_demand = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi/"+inputs['location_aux'], sep=',')   

        arraysConsumption={'dayArray':dayArray,'weekArray':weekArray,'monthArray':monthArray}
        inputs.update(arraysConsumption)
            
        ## FINANCE
        businessModel=inputs['businessModel'] #Type of business model
        fuel=inputs['currentFuel'] #Type of fuel used
        Fuel_price=inputs['fuelPrice']   #Price of fossil fuel [€/kWh]
        co2TonPrice=inputs['co2TonPrice'] #[€/ton]
        co2factor=inputs['co2factor'] #[-]
         
    elif origin==-3: #Simulation called from CIMAV's front end
        
        #Retrieve front-end inputs
        [inputs,annualConsumptionkWh,P_op_bar,monthArray,weekArray,dayArray]=djangoReportCIMAV(inputsDjango)
        
        ## METEO
        localMeteo=inputsDjango['location']#posiblemente se pueda borrar después
        file_loc_list=[os.path.dirname(os.path.dirname(__file__)),'CIMAV/meteorologic_database',inputsDjango['pais'],inputsDjango['location']] #Stores the localization of the TMY as a list=[basedir,TMYlocalizationfolder,countryfolder,TMYcity]
        file_loc='/'.join(file_loc_list) #Converts file_loc_list into a single string for later use
        Lat,Huso,Positional_longitude=Lat_Huso(file_loc) #Calls a function wich reads only the line where the Lat and Timezone is and gives back theit values for the right city
        
        ## INTEGRATION
        type_integration=desginDict['type_integration'] # Type of integration scheme from IEA SHC Task 49 "Integration guidelines" http://task49.iea-shc.org/Data/Sites/7/150218_iea-task-49_d_b2_integration_guideline-final.pdf
        almVolumen=desginDict['almVolumen'] # Storage capacity [litres]
        
        ## INDUSTRIAL APPLICATION
            #>> PROCESS
        fluidInput=inputsDjango['fluid'] #Type of fluid 
        T_process_in=inputsDjango['tempOUT'] #HIGH - Process temperature [ºC]
        T_process_out=inputsDjango['tempIN'] #LOW - Temperature at the return of the process [ºC]
        #P_op_bar=P_op_bar #[bar]
        
            #>> ENERGY DEMAND 
        file_demand=demandCreator(annualConsumptionkWh,dayArray,weekArray,monthArray)
       
        ## FINANCE
        businessModel=inputsDjango['businessModel'] #Type of business model
        fuel=inputsDjango['fuel'] #Type of fuel used
        Fuel_price=inputsDjango['fuelPrice'] #Price of fossil fuel [mxn/kWh] transformed the units in the views.py
        co2TonPrice= inputsDjango['co2TonPrice'] #[mxn/ton]
        co2factor=inputsDjango['co2factor'] #[-]
        
    elif origin==1: #Simulation called from external front-end. Available from 1 to inf+
        
        #Retrieve front-end inputs 
        if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
            [inputs,annualConsumptionkWh,P_op_bar,monthArray,weekArray,dayArray]=djangoReport2(inputsDjango,simControl['itercontrol'])
        else:
            [inputs,annualConsumptionkWh,P_op_bar,monthArray,weekArray,dayArray]=djangoReport(inputsDjango)
        ## METEO (free available meteo sets)
        locationFromFrontEnd=inputs['location']
        
        if sender=='solatom': #Use Solatom propietary meteo DB. This is only necessary to be able to use solatom data from terminal
            meteoDB = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/meteoDB.csv", sep=',') 
            file_loc=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/"+localMeteo       
            Lat=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Latitud'].iloc[0]
            Huso=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Huso'].iloc[0]
        elif sender=='SHIPcal':
            from simforms.models import Locations
            file_loc = locationFromFrontEnd
            localMeteo= Locations.objects.get(pk=locationFromFrontEnd).city
            Lat = Locations.objects.get(pk=locationFromFrontEnd).lat
            Huso = 0 #Not used currently, it is assumed to have solar hourly data
            #meteo_data.order_by('hour_year_sim').values_list('DNI',flat=True)
            long = Locations.objects.get(pk=locationFromFrontEnd).lon
        else:
            meteoDB = pd.read_csv(os.path.dirname(__file__)+"/Meteo_modules/meteoDB.csv", sep=',')  
            localMeteo=meteoDB.loc[meteoDB['Provincia'] == locationFromFrontEnd, 'meteoFile'].iloc[0]
            file_loc=os.path.dirname(__file__)+"/Meteo_modules/"+localMeteo
            Lat=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Latitud'].iloc[0]
            Huso=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Huso'].iloc[0]
            long=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Long'].iloc[0]
        
        ## INTEGRATION
        type_integration=desginDict['type_integration'] # Type of integration scheme from IEA SHC Task 49 "Integration guidelines" http://task49.iea-shc.org/Data/Sites/7/150218_iea-task-49_d_b2_integration_guideline-final.pdf
        almVolumen=desginDict['almVolumen'] # Storage capacity [litres]
        
        ## INDUSTRIAL APPLICATION
            #>> PROCESS
        fluidInput=inputs['fluid'] #Type of fluid 
        T_process_in=inputs['outletTemp'] #HIGH - Process temperature [ºC]
        T_process_out=inputs['inletTemp'] #LOW - Temperature at the return of the process [ºC]
        P_op_bar=P_op_bar #[bar]
            
            #>> ENERGY DEMAND
        ten_minArray=[1/6,1/6,1/6,1/6,1/6,1/6]
        fifteen_minArray=[1/4,1/4,1/4,1/4]
        if simControl['itercontrol']=='paso_10min':
            file_demand=demandCreator2(annualConsumptionkWh,dayArray,weekArray,monthArray,ten_minArray,simControl['itercontrol'])
        elif simControl['itercontrol']=='paso_15min':
            file_demand=demandCreator2(annualConsumptionkWh,dayArray,weekArray,monthArray,fifteen_minArray,simControl['itercontrol'])
        else:
            file_demand=demandCreator(annualConsumptionkWh,dayArray,weekArray,monthArray)
       
        arraysConsumption={'dayArray':dayArray,'weekArray':weekArray,'monthArray':monthArray}
        inputs.update(arraysConsumption)
            
        ## FINANCE
        businessModel=inputs['businessModel'] #Type of business model
        fuel=inputs['currentFuel'] #Type of fuel used
        Fuel_price=inputs['fuelPrice']   #Price of fossil fuel [€/kWh]
        co2TonPrice=inputs['co2TonPrice'] #[€/ton]
        co2factor=inputs['co2factor'] #[-]
         
                  
    elif origin==0:  #Simulation called from Python file (called from the terminal)
        
        ## METEO
#        localMeteo="Fargo_SAM.dat" #Be sure this location is included in SHIPcal DB
        localMeteo="Sevilla10min.dat"
        if sender=='solatom': #Use Solatom propietary meteo DB. This is only necessary to be able to use solatom data from terminal
            meteoDB = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/meteoDB.csv", sep=',') 
            file_loc=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/"+localMeteo       
            Lat=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Latitud'].iloc[0]
            Huso=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Huso'].iloc[0]
        else:
            if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                meteoDB = pd.read_csv(os.path.dirname(__file__)+"/Meteo_modules/meteoDB3.csv", sep=',')  
                file_loc=os.path.dirname(__file__)+"/Meteo_modules/"+localMeteo
                Lat=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Latitud'].iloc[0]
                Huso=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Huso'].iloc[0]
                long=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Long'].iloc[0]
            
                
            else:
                meteoDB = pd.read_csv(os.path.dirname(__file__)+"/Meteo_modules/meteoDB3.csv", sep=',')  
                file_loc=os.path.dirname(__file__)+"/Meteo_modules/"+localMeteo
                Lat=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Latitud'].iloc[0]
                Huso=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Huso'].iloc[0]
                long=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Long'].iloc[0]
        
        ## INTEGRATION
        type_integration=desginDict['type_integration'] # Type of integration scheme from IEA SHC Task 49 "Integration guidelines" http://task49.iea-shc.org/Data/Sites/7/150218_iea-task-49_d_b2_integration_guideline-final.pdf
        almVolumen=desginDict['almVolumen'] # Storage capacity [litres]    
        
        ## INDUSTRIAL APPLICATION
            #>> PROCESS
        fluidInput="water" #"water" "steam" "oil" "moltenSalt"
        T_process_in=140 #HIGH - Process temperature [ºC]
        T_process_out=80 #LOW - Temperature at the return of the process [ºC]
        P_op_bar=16 #[bar] 
        
        # Not implemented yet
        """
        distanceInput=15 #From the solar plant to the network integration point [m]
        surfaceAvailable=500 #Surface available for the solar plant [m2]
        """
            
        ## ENERGY DEMAND
#        dayArray=[0,0,0,0,0,0,0,1/10,1/10,1/10,1/10,1/10,1/10,1/10,1/10,1/10,1/10,1/10,0,0,0,0,0,0] #12 hours day profile
        ten_minArray=[1/6,1/6,1/6,1/6,1/6,1/6]
        fifteen_minArray=[1/4,1/4,1/4,1/4]
        dayArray=[1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24] #24 hours day profile
       
        weekArray=[0.143,0.143,0.143,0.143,0.143,0.143,0.143] #No weekends
        monthArray=[1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12] #Whole year     
        totalConsumption=900*8760 #[kWh]
        if simControl['itercontrol']=='paso_10min':
            file_demand=demandCreator2(totalConsumption,dayArray,weekArray,monthArray,ten_minArray,simControl['itercontrol'])
        elif simControl['itercontrol']=='paso_15min':
            file_demand=demandCreator2(totalConsumption,dayArray,weekArray,monthArray,fifteen_minArray,simControl['itercontrol'])
        else:
            file_demand=demandCreator(totalConsumption,dayArray,weekArray,monthArray)
        # file_demand = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi_offline/demand_files/demand_con.csv", sep=',')      

        ## FINANCE
        businessModel="turnkey"
        fuel="Gasoil-B" #Type of fuel
        Fuel_price=0.05 #Price of fossil fuel 1st year of simulation [€/kWh]
        co2TonPrice=0 #[€/TonCo2]
        co2factor=1 #Default value 1, after it will be modified [-]

        #CO2 factors of the different fuels availables (Usually it is taken care by the front-end but here, since the simulation is not called from a front-end, it has to be calculated)
        if fuel in ["NG","LNG"]:
            co2factor=.2/1000 #[TonCo2/kWh]  #https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html
        if fuel in ['Fueloil2','Fueloil3','Gasoil-B','Gasoil-C']:
            co2factor=.27/1000 #[TonCo2/kWh]       #https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html    
        if fuel in ['Electricity']:
            co2factor=.385/1000 #[TonCo2/kWh]  #https://www.eia.gov/tools/faqs/faq.php?id=74&t=11
        if fuel in ['Propane','Butane','Air-propane']:
            co2factor=.22/1000 #[TonCo2/kWh]    #https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html  
        if fuel in ['Biomass']:
            co2factor=.41/1000 #[TonCo2/kWh]  #https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html

    #Demand of energy before the boiler
    if simControl['itercontrol']=='paso_10min':
        Energy_Before=DemandData2(file_demand,month_ini_sim,day_ini_sim,hour_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim, ten_min_ini_sim, ten_min_fin_sim, simControl['itercontrol']) # [kWh]
    
    elif simControl['itercontrol']=='paso_15min':
        Energy_Before=DemandData2(file_demand,month_ini_sim,day_ini_sim,hour_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim, fifteen_min_ini_sim, fifteen_min_fin_sim, simControl['itercontrol']) # [kWh]
        
    else:
        Energy_Before=DemandData(file_demand,month_ini_sim,day_ini_sim,hour_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim) # [kWh]
    Energy_Before_annual=sum(Energy_Before) #This should be exactly the same as annualConsumptionkWh for annual simulations
    Demand=Boiler_eff*Energy_Before #Demand of energy after the boiler [kWh]
    
    
    if co2TonPrice>0:
        CO2=1 #Flag to take into account co2 savings in terms of cost per ton emitted
    else:
        CO2=0 #Flag to take into account co2 savings in terms of cost per ton emitted
    
    
    # --> Meteo variables
    if simControl['itercontrol']=='paso_10min':
       output,i_initial,i_final=SolarData2(file_loc,month_ini_sim,day_ini_sim,hour_ini_sim,ten_min_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim,ten_min_fin_sim, simControl['itercontrol'],huso,simControl['to_solartime'],long,sender,Lat,Huso)
    elif simControl['itercontrol']=='paso_15min':
       output,i_initial,i_final=SolarData2(file_loc,month_ini_sim,day_ini_sim,hour_ini_sim,fifteen_min_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim,fifteen_min_fin_sim, simControl['itercontrol'],huso,simControl['to_solartime'],long,sender,Lat,Huso)
    elif localMeteo=="Sevillahorario.dat":
       output,i_initial,i_final=SolarData3(simControl['to_solartime'],long,huso,file_loc,month_ini_sim,day_ini_sim,hour_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim,sender,Lat,Huso) 
    else:
        output,i_initial,i_final=SolarData(file_loc,month_ini_sim,day_ini_sim,hour_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim,sender,Lat,Huso)
    
    """
    Output key:
    output[0]->month of year
    output[1]->day of month
    output[2]->hour of day
    output[3]->hour of year
    output[4]->W - rad
    output[5]->SUN_ELV - rad
    output[6]->SUN AZ - rad
    output[7]->DECL - rad
    output[8]->SUN ZEN - rad
    output[9]->DNI  - W/m2
    output[10]->temp -C
    output[11]->step_sim
    
    In case the iterations are minutes´s portions:
    
        
    Output key:
    output[0]->month of year
    output[1]->day of month
    output[2]->hour of day
    output[3]-> minutes portions of hour
    output[4]-> minutes portions of the year
    output[5]->W - rad
    output[6]->SUN_ELV - rad
    output[7]->SUN AZ - rad
    output[8]->DECL - rad
    output[9]->SUN ZEN - rad
    output[10]->DNI  - W/m2
    output[11]->temp -C
    output[12]->step_sim
    
            
    """
    if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
        SUN_ELV=output[:,6] # Sun elevation [rad]
        SUN_AZ=output[:,7] # Sun azimuth [rad]
        DNI=output[:,10] # Direct Normal Irradiation [W/m²]
        temp=output[:,11]+273 # Ambient temperature [K] 
        step_sim=output [:,12] #Array containing the simulation steps 
        steps_sim=len(output) # Number of steps in the simulation
    
    else:
        SUN_ELV=output[:,5] # Sun elevation [rad]
        SUN_AZ=output[:,6] # Sun azimuth [rad]
        DNI=output[:,9] # Direct Normal Irradiation [W/m²]
        temp=output[:,10]+273 # Ambient temperature [K] 
        step_sim=output [:,11] #Array containing the simulation steps 
        steps_sim=len(output) # Number of steps in the simulation

    
    DNI=DNI*mofDNI # DNI modified if needed. This is necessary to take into account 
    meteoDict={'DNI':DNI.tolist(),'localMeteo':localMeteo}
    
    #Temperature of the make-up water
    
    if simControl['itercontrol']=='paso_10min' :
    
        T_in_C_AR=waterFromGrid_v3_min(file_loc,itercontrol,sender)
        T_in_C_AR=waterFromGrid_trim2(T_in_C_AR,month_ini_sim,day_ini_sim,hour_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim,ten_min_ini_sim,ten_min_fin_sim)
    elif simControl['itercontrol']=='paso_15min':
        T_in_C_AR=waterFromGrid_v3_min(file_loc,itercontrol,sender)
        T_in_C_AR=waterFromGrid_trim2(T_in_C_AR,month_ini_sim,day_ini_sim,hour_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim,fifteen_min_ini_sim,fifteen_min_fin_sim)
    else:
        T_in_C_AR=waterFromGrid_v3(file_loc,sender)
        #Trim the T_in_C_AR [8760] to the simulation frame 
        T_in_C_AR=waterFromGrid_trim(T_in_C_AR,month_ini_sim,day_ini_sim,hour_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim)


#%%
# ------------------------------------------------------------------------------------
# BLOCK 2 - SOLAR SIMULATION --------------------------------------------------
# ------------------------------------------------------------------------------------
    # BLOCK 2.1 - PROCESS VARIABLES <><><><><><><><><><><><><><><><><><><><><><><><><><><>      
    # IEA SHC Task 49 "Integration guidelines" http://task49.iea-shc.org/Data/Sites/7/150218_iea-task-49_d_b2_integration_guideline-final.pdf

    # --> Process variable at design point
    
    sat_liq=0 #Not used
    sat_vap=0 #Not used
    x_design=0 #Not used
    h_process_in=0 #Not used
    energStorageMax=0 #kWh
    energy_stored=0 #kWh
    porctSensible=0 #Not used
    T_out_HX_C=0 #Not used 
    T_process_in_C=0 #Not used
    T_process_out_C=0 #Not used
    s_process_in=0 #Not used
    h_process_in=0 #Not used
    SD_min_energy=0 #For plotting
    SD_max_energy=0 #For plotting
    in_s=0
    out_s=0
    h_in=0
    h_out=0
    
    
    
    #By default water flows in closed loop
    T_in_flag=1 #Flag 1 means closed loop (water flowing from a piping closed loop); Flag 0 means open loop (water flowing from the grid)
    
    if sender=='CIMAV':
        T_in_flag=inputsDjango['T_in_flag'] #Flag 1 means closed loop (water flowing from a piping closed loop); Flag 0 means open loop (water flowing from the grid)
        if T_in_flag == 0:        
            T_process_out = np.average(T_in_C_AR)
    # --> Integrations: 
        # SL_L_RF Supply level with liquid heat transfer media solar return flow boost
        
    if type_integration=="SL_L_RF": 

        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        
        #Outlet of the process
        T_process_out_C=T_process_out
        T_process_out_K=T_process_out_C+273
        if fluidInput=="water": 
            output_ProcessState=IAPWS97(P=P_op_Mpa, T=T_process_out_K)
            h_process_out=output_ProcessState.h
        #Inlet of the process
        if fluidInput=="water":    
            if T_process_in>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                T_process_in=IAPWS97(P=P_op_Mpa, x=0).T-273
        T_process_in_C=T_process_in
        T_process_in_K=T_process_in_C+273
        if fluidInput=="water": 
            input_ProcessState=IAPWS97(P=P_op_Mpa, T=T_process_in_K)
            s_process_in=input_ProcessState.s
            h_process_in=input_ProcessState.h
        T_av_process_K=(T_process_out_K+T_process_in_K)/2
        
        # --------------  STEP 1 -------------- 
            #The inlet temperature at the solar field (Afterwards it will corrected to take into account the HX) 
        T_in_C=T_process_out_C #The inlet temperature at the solar field is the same than the return of the process
        T_in_K=T_in_C+273
        
            #The outlet temperature at the solar field (Afterwards it will corrected to take into account the HX) 
        T_out_C=T_process_in_C #The outlet temperature at the solar field is the same than the process temperature
        T_out_K=T_out_C+273
        
    ##Heat Exchanger design 
        # --------------  STEP 2 -------------- 
            #HX inlet (process side)         
        T_in_C=T_process_out_C #Already defined before
        # --------------  STEP 3 -------------- 
            #HX outlet (process side) 
        T_HX_out_K=(T_process_out_K+(T_process_in_K-T_process_out_K)*heatFactor)
        T_out_HX_C=T_HX_out_K-273
        if fluidInput=="water": 
            outputHXState=IAPWS97(P=P_op_Mpa, T=T_HX_out_K)
            h_HX_out=outputHXState.h    
          # --------------  STEP 4 -------------- 
            #HX inlet (solar side) 
        T_out_P=T_HX_out_K+DELTA_HX-273  # Design point temperature at the inlet of the HX from the solar side
        T_out_C=T_out_P #T_out_C is updated
        T_out_K=T_out_C+273    
         # --------------  STEP 5 -------------- 
            #HX outlet (solar side)        
        T_in_P=T_in_C+DELTA_HX  # Design point temperature at the outlet of the HX from the solar side
        T_in_C=T_in_P #T_in_C is updated
        T_in_K=T_in_C+273
        
        #Other auxiliar calculations necessary  (for plotting)
        if fluidInput=="water": 
            inputState=IAPWS97(P=P_op_Mpa, T=T_in_K) 
            h_in=inputState.h    
            in_s=inputState.s
            in_x=inputState.x
            outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
            out_s=outputState.s
            h_out=outputState.h                                                                                                                                                                                  
            
    
    # ----------------------------------------
        # SL_L_P => Supply level with liquid heat transfer media parallel integration
        # PL_E_PM => Process level external HEX for heating of product or process medium
        
    elif type_integration=="SL_L_P" or type_integration=="PL_E_PM" :   
           
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        
        #Outlet of the process
        T_process_out_C=T_process_out
        T_process_out_K=T_process_out_C+273
        if fluidInput=="water": 
            output_ProcessState=IAPWS97(P=P_op_Mpa, T=T_process_out_K)
            h_process_out=output_ProcessState.h
        
        #Inlet of the process
        if fluidInput=="water":    
            if T_process_in>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                T_process_in=IAPWS97(P=P_op_Mpa, x=0).T-273   
        T_process_in_C=T_process_in
        T_process_in_K=T_process_in_C+273
        if fluidInput=="water": 
            input_ProcessState=IAPWS97(P=P_op_Mpa, T=T_process_in_K)
            s_process_in=input_ProcessState.s
            h_process_in=input_ProcessState.h
        T_av_process_K=(T_process_out_K+T_process_in_K)/2
        
        
        # --------------  STEP 1 -------------- 
            #The inlet temperature at the solar field 
        T_in_C=T_process_out_C #The inlet temperature at the solar field is the same than the return of the process
        T_in_K=T_in_C+273


            #The outlet temperature at the solar field 
        T_out_C=T_process_in_C #The outlet temperature at the solar field is the same than the process temperature
        T_out_K=T_out_C+273

        
        #Other auxiliar calculations necessary  (for plotting)
        if fluidInput=="water":
            
            inputState=IAPWS97(P=P_op_Mpa, T=T_in_K) 
            h_in=inputState.h    
            in_s=inputState.s
            in_x=inputState.x
            outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
            out_s=outputState.s
            h_out=outputState.h
        
    # ----------------------------------------
        # SL_L_S => Supply level with liquid heat transfer media solar heating of storages
        # SL_L_S_PH => Supply level with liquid heat transfer media solar heating of storages (Preheating)
        
    elif type_integration=="SL_L_S" or type_integration=="SL_L_S_PH":
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        
        # --------------  STEP 1 -------------- 
            #The inlet temperature at the solar field 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
        T_in_K=T_in_C+273
            
            #The outlet temperature at the solar field 
        T_out_C=T_process_in #The outlet temperature at the solar field is the same than the process temperature
        if fluidInput=="water": # Only applies to water
            if T_out_C>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                T_out_C=IAPWS97(P=P_op_Mpa, x=0).T-273-subcooling
        T_out_K=T_out_C+273
        
        # --------------  STEP 2 -------------- 
        T_ini_storage=T_in_K #Initial temperature of the storage
        
        # --------------  STEP 3 -------------- 
        T_min_storage=T_out_K #MIN temperature storage to supply to the process # Process temp [K]  
        if type_integration=="SL_L_S_PH":
            T_min_storage=T_in_K #MIN [K] When preheating the minimum temp is the process outlet    
        
        # --------------  STEP 4 -------------- 
        if type_integration=="SL_L_S":
            if fluidInput=="water": # Only applies to water
                if T_out_C+DELTA_ST>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                    T_max_storage=IAPWS97(P=P_op_Mpa, x=0).T -subcooling #Max temperature storage [K]
                else:
                    T_max_storage=T_out_C+DELTA_ST+273 #Max temperature storage [K]
            else:
                T_max_storage=T_out_C+DELTA_ST+273 #Max temperature storage [K]
        else:
            if fluidInput=="water": # Only applies to water
                if T_out_C>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                    T_max_storage=IAPWS97(P=P_op_Mpa, x=0).T -subcooling #Max temperature storage [K]
                else:
                    T_max_storage=T_out_C+273 #Max temperature storage [K]
            else:
                T_max_storage=T_out_C+273 #Max temperature storage [K]
        
        
        # --------------  STEP 5 -------------- 
        energy_stored=0 # Initially the storage is empty
        
        if fluidInput=="water": # WATER STORAGE
            inputState=IAPWS97(P=P_op_Mpa, T=T_in_K) 
            h_in=inputState.h
            in_s=inputState.s
            in_x=inputState.x
            outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
            out_s=outputState.s
            h_out=outputState.h
            
            T_avg_K=(T_in_K+T_out_K)/2
            
            almacenamiento=IAPWS97(P=P_op_Mpa, T=T_max_storage) #Propiedades en el almacenamiento
            almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
            almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg          
            storage_max_energy=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_max_storage))/3600 #Storage capacity in kWh
            
            almacenamiento=IAPWS97(P=P_op_Mpa, T=T_in_K) #Propiedades en el almacenamiento
            almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
            almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg      
            
            storage_ini_energy=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_in_K))/3600 #Storage capacity in kWh
            
            almacenamiento=IAPWS97(P=P_op_Mpa, T=T_out_K) #Propiedades en el almacenamiento
            almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
            almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg      
            storage_min_energy=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_out_K))/3600 #Storage capacity in kWh
            
            if type_integration=="SL_L_S_PH":
                almacenamiento=IAPWS97(P=P_op_Mpa, T=T_in_K) #Propiedades en el almacenamiento
                almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
                almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg 
                storage_min_energy=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_in_K))/3600 #Storage capacity in kWh
            
            energStorageUseful=storage_max_energy-storage_min_energy # Maximum storage capacity in kWh
            energStorageMax=storage_max_energy-storage_ini_energy # Maximum storage capacity in kWh
        
        elif fluidInput=="oil": # THERMAL OIL STORAGE

            T_avg_K=(T_in_K+T_out_K)/2
            
            # Properties for MAX point
                 
            [storage_max_rho,storage_max_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_max_storage)
            storage_max_energy=(almVolumen*(1/1000)*(storage_max_rho)*storage_max_Cp*(T_max_storage))/3600 #Storage capacity in kWh
            
            [storage_ini_rho,storage_ini_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_in_K)
            storage_ini_energy=(almVolumen*(1/1000)*(storage_ini_rho)*storage_ini_Cp*(T_in_K))/3600 #Storage capacity in kWh
        
            [storage_min_rho,storage_min_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_out_K)
            storage_min_energy=(almVolumen*(1/1000)*(storage_min_rho)*storage_min_Cp*(T_out_K))/3600 #Storage capacity in kWh
            
            if type_integration=="SL_L_S_PH":
                [storage_min_rho,storage_min_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_in_K)
                storage_min_energy=(almVolumen*(1/1000)*(storage_min_rho)*storage_min_Cp*(T_in_K))/3600 #Storage capacity in kWh
            
            energStorageUseful=storage_max_energy-storage_min_energy # Maximum storage capacity in kWh
            energStorageMax=storage_max_energy-storage_ini_energy # Maximum storage capacity in kWh
    
        elif fluidInput=="moltenSalt": # MOLTEN SALTS STORAGE
                       
            T_avg_K=(T_in_K+T_out_K)/2
            
            # Properties for MAX point
            [storage_max_rho,storage_max_Cp,k,Dv]=moltenSalt(T_max_storage)
            storage_max_energy=(almVolumen*(1/1000)*(storage_max_rho)*storage_max_Cp*(T_max_storage))/3600 #Storage capacity in kWh
            
            [storage_ini_rho,storage_ini_Cp,k,Dv]=moltenSalt(T_in_K)
            storage_ini_energy=(almVolumen*(1/1000)*(storage_ini_rho)*storage_ini_Cp*(T_in_K))/3600 #Storage capacity in kWh
        
            [storage_min_rho,storage_min_Cp,k,Dv]=moltenSalt(T_out_K)
            storage_min_energy=(almVolumen*(1/1000)*(storage_min_rho)*storage_min_Cp*(T_out_K))/3600 #Storage capacity in kWh
            
            if type_integration=="SL_L_S_PH":
                [storage_min_rho,storage_min_Cp,k,Dv]=moltenSalt(T_in_K)
                storage_min_energy=(almVolumen*(1/1000)*(storage_min_rho)*storage_min_Cp*(T_in_K))/3600 #Storage capacity in kWh
            
            energStorageUseful=storage_max_energy-storage_min_energy # Maximum storage capacity in kWh    
            energStorageMax=storage_max_energy-storage_ini_energy # Maximum storage capacity in kWh
    
        # ----------------------------------------
        # SL_L_PS => Supply level with liquid heat transfer media parallel integration with storage
        
    elif type_integration=="SL_L_PS":
              
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
        T_out_C=T_process_in #The outlet temperature at the solar field is the same than the process temperature

        
        T_in_K=T_in_C+273
        
        if fluidInput=="water":
            if T_out_C>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                T_out_C=IAPWS97(P=P_op_Mpa, x=0).T-273
            T_out_K=T_out_C+273
            #tempAlm=T_out_K-273
            inputState=IAPWS97(P=P_op_Mpa, T=T_in_K) 
            h_in=inputState.h
            in_s=inputState.s
            in_x=inputState.x
            outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
            out_s=outputState.s
            h_out=outputState.h
            
            #Storage calculations for water
            energy_stored=0 #Initial storage
            T_avg_K=(T_in_K+T_out_K)/2
            almacenamiento=IAPWS97(P=P_op_Mpa, T=T_avg_K) #Propiedades en el almacenamiento
            almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
            almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg
            energStorageMax=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_out_K-T_in_K))/3600 #Storage capacity in kWh
        
        elif fluidInput=="oil":
            T_out_K=T_out_C+273
            energy_stored=0 #Initial storage
            T_av_K=(T_in_K+T_out_K)/2
            [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
            energStorageMax=(almVolumen*(1/1000)*(rho_av)*Cp_av*(T_out_K-T_in_K))/3600 #Storage capacity in kWh
        
        elif fluidInput=="moltenSalt":
            T_out_K=T_out_C+273
            energy_stored=0 #Initial storage
            T_av_K=(T_in_K+T_out_K)/2
            [rho_av,Cp_av,k,Dv]=moltenSalt(T_av_K)
            energStorageMax=(almVolumen*(1/1000)*(rho_av)*Cp_av*(T_out_K-T_in_K))/3600 #Storage capacity in kWh
                
    # ---------------------------------------- 
        # SL_S_FW => Supply level with steam solar heating of boiler feed water
        
    elif type_integration=="SL_S_FW":
        
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
        T_out_C=T_process_in #The outlet temperature at the solar field is the same than the process temperature
        
        energStorageMax=0 #kWh
        energy_stored=0 #kWh
        T_in_K=T_in_C+273
        initial=IAPWS97(P=P_op_Mpa, T=T_in_K)
        h_in=initial.h #kJ/kg
        in_x=initial.x
        sat_liq=IAPWS97(P=P_op_Mpa, x=0)
        sat_vap=IAPWS97(P=P_op_Mpa, x=1)
        h_sat_liq=sat_liq.h
        h_sat_vap=sat_vap.h
        sensiblePart=h_sat_liq-h_in
        latentPart=h_sat_vap-h_sat_liq
        total=h_sat_vap-h_in
        porctSensible=sensiblePart/total
        porctLatent=latentPart/total
        Demand2=Demand*porctSensible
        
        T_out_K=IAPWS97(P=P_op_Mpa, x=0).T-subcooling #Heating point
        T_out_C=T_out_K-273 
          
        in_s=initial.s
        outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
        out_s=outputState.s
        h_out=outputState.h
    
    # ----------------------------------------
    # SL_S_FWS => Supply level with steam solar heating of boiler feed water including storage
    
    elif type_integration=="SL_S_FWS":
            
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
              
        T_out_K=IAPWS97(P=P_op_Mpa, x=0).T #Heating point
        T_out_C=T_out_K-273 
        
        outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
        out_s=outputState.s
        h_out=outputState.h
        

        T_in_K=T_in_C+273

            
        initial=IAPWS97(P=P_op_Mpa, T=T_in_K)
        h_in=initial.h #kJ/kg
        in_s=initial.s
        in_x=initial.x
        sat_liq=IAPWS97(P=P_op_Mpa, x=0)
        sat_vap=IAPWS97(P=P_op_Mpa, x=1)
        h_sat_liq=sat_liq.h
        h_sat_vap=sat_vap.h
        sensiblePart=h_sat_liq-h_in
        latentPart=h_sat_vap-h_sat_liq
        PreHeatedPart=h_out-h_in
        total=h_sat_vap-h_in
        
        porctSensible=sensiblePart/total
        porctLatent=latentPart/total
        porctPreHeated=PreHeatedPart/total
        Demand2=Demand*porctPreHeated
        
        T_avg_K=(T_in_K+T_out_K)/2
#        tempAlm=T_out_K-273
        almacenamiento=IAPWS97(P=P_op_Mpa, T=T_avg_K) #Propiedades en el almacenamiento
        almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
        almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg
        energStorageMax=almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_out_K-T_in_K)/3600 #Storage capacity in kWh
        energy_stored=0 #Initial storage
        
    # ---------------------------------------- 
        # SL_S_MW => Supply level with steam solar heating of boiler make-up water
        
    elif type_integration=="SL_S_MW":
 
        T_in_flag=0 #Flag 1 means closed loop (water flowing from a piping closed loop); Flag 0 means open loop (water flowing from the grid)
        
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
        T_out_C=T_process_in #The outlet temperature at the solar field is the same than the process temperature
        
        energStorageMax=0 #kWh
        energy_stored=0 #kWh
        T_in_K=T_in_C+273
        initial=IAPWS97(P=P_op_Mpa, T=T_in_K)
        h_in=initial.h #kJ/kg
        in_x=initial.x
        sat_liq=IAPWS97(P=P_op_Mpa, x=0)
        sat_vap=IAPWS97(P=P_op_Mpa, x=1)
        h_sat_liq=sat_liq.h
        h_sat_vap=sat_vap.h
        sensiblePart=h_sat_liq-h_in
        latentPart=h_sat_vap-h_sat_liq
        total=h_sat_vap-h_in
        porctSensible=sensiblePart/total
        porctLatent=latentPart/total
        Demand2=Demand*porctSensible
        
        T_out_K=IAPWS97(P=P_op_Mpa, x=0).T-subcooling #Heating point
        T_out_C=T_out_K-273 
          
        in_s=initial.s
        outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
        out_s=outputState.s
        h_out=outputState.h
    
    # ----------------------------------------
    #SL_S_MWS => Supply level with steam solar heating of boiler make-up water including storage
    
    elif type_integration=="SL_S_MWS":
        
        T_in_flag=0 #Flag 1 means closed loop (water flowing from a piping closed loop); Flag 0 means open loop (water flowing from the grid)
        
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
              
        T_out_K=IAPWS97(P=P_op_Mpa, x=0).T #Heating point
        T_out_C=T_out_K-273 
        
        outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
        out_s=outputState.s
        h_out=outputState.h
        
        if T_in_flag==1:
            T_in_K=T_in_C+273
        else:
            T_in_K=np.average(T_in_C_AR)+273
            
        initial=IAPWS97(P=P_op_Mpa, T=T_in_K)
        h_in=initial.h #kJ/kg
        in_s=initial.s
        in_x=initial.x
        in_x=in_x
        sat_liq=IAPWS97(P=P_op_Mpa, x=0)
        sat_vap=IAPWS97(P=P_op_Mpa, x=1)
        h_sat_liq=sat_liq.h
        h_sat_vap=sat_vap.h
        sensiblePart=h_sat_liq-h_in
        latentPart=h_sat_vap-h_sat_liq
        PreHeatedPart=h_out-h_in
        total=h_sat_vap-h_in
        
        porctSensible=sensiblePart/total
        porctLatent=latentPart/total
        porctLatent=porctLatent
        porctPreHeated=PreHeatedPart/total
        Demand2=Demand*porctPreHeated
        
        T_avg_K=(T_in_K+T_out_K)/2
#        tempAlm=T_out_K-273
        almacenamiento=IAPWS97(P=P_op_Mpa, T=T_avg_K) #Propiedades en el almacenamiento
        almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
        almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg
        energStorageMax=almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_out_K-T_in_K)/3600 #Storage capacity in kWh
        energy_stored=0 #Initial storage
    
    # ----------------------------------------
        # SL_S_PD_OT => Supply level with steam direct solar steam generation once-thorugh
        
    elif type_integration=="SL_S_PD_OT":
        
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        
        # Outlet of the process
        T_process_out_C=T_process_out
        T_process_out_K=T_process_out_C+273

        #Inlet of the process
        input_ProcessState=IAPWS97(P=P_op_Mpa, x=1)
        T_process_in_K=input_ProcessState.T
        T_process_in_C=T_process_in_K-273
        
        s_process_in=input_ProcessState.s
        h_process_in=input_ProcessState.h

        # --------------  STEP 1 -------------- 
            #The inlet temperature at the solar field 
        T_in_C=T_process_out_C #The inlet temperature at the solar field is the same than the return of the process
        T_in_K=T_in_C+273

        sat_liq=IAPWS97(P=P_op_Mpa, x=0)

        if T_in_K>sat_liq.T: #Ensure the inlet is in liquid phase
            T_in_K=sat_liq.T  

        initial=IAPWS97(P=P_op_Mpa, T=T_in_K)
        h_in=initial.h #kJ/kg
        in_s=initial.s
        
            #The outlet temperature at the solar field 
        T_out_K=input_ProcessState.T 
        T_out_C=input_ProcessState.T-273 #Temperature of saturation at that level
        
        # --------------  STEP 2 --------------
        # Design point   
        x_design=0.8 #Design steam quality

        outputState=IAPWS97(P=P_op_Mpa, x=x_design)
        out_s=outputState.s
        h_out=outputState.h
        
    elif type_integration=="SL_S_PD": #Direct steam generation (Steam drum)
        
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
       
        # Outlet of the process
        T_process_out_C=T_process_out
        T_process_out_K=T_process_out_C+273

        #Inlet of the process
        input_ProcessState=IAPWS97(P=P_op_Mpa, x=1)
        T_process_in_K=input_ProcessState.T
        T_process_in_C=T_process_in_K-273
        
        s_process_in=input_ProcessState.s
        h_process_in=input_ProcessState.h

        # --------------  STEP 1 -------------- 
            #The inlet temperature at the steam drum 
        T_SD_in_C=T_process_out_C #The inlet temperature at the solar field is the same than the return of the process
        T_SD_in_K=T_SD_in_C+273
        sat_liq=IAPWS97(P=P_op_Mpa, x=0)

        if T_SD_in_K>sat_liq.T: #Ensure the inlet is in liquid phase
            T_SD_in_K=sat_liq.T  

        initial=IAPWS97(P=P_op_Mpa, T=T_SD_in_K)
        #h_SD_in=initial.h #kJ/kg
        #in_SD_s=initial.s
        
            #The outlet temperature at the steam drum
        #T_SD_out_K=sat_liq.T
        #T_SD_out_C=T_SD_out_K-273 #Temperature of saturation at that level
        
        # --------------- STEP 2 ---------------
        #Steam drum properties
        SD_mass=200*int(num_modulos_tot/4) #mass in the steam drum [kg]
        
        #Limit conditions
        SD_limit_energy=SD_mass*IAPWS97(P=P_op_Mpa, T=283).h/3600 #Inf. Limit temperature for the steam drum in kWh
        #Minimum conditions
        SD_min_energy=SD_mass*IAPWS97(P=P_op_Mpa, x=0.2).h/3600 #Min temperature for the steam drum in kWh
        #Maximum conditions
        SD_max_energy=SD_mass*IAPWS97(P=P_op_Mpa, x=0.6).h/3600 #Min temperature for the steam drum in kWh
             
        
        PerdSD=(SD_min_energy-SD_limit_energy)/48 # SD ambient Loss Kwh - All energy is lost after 2 days
        
        # --------------- STEP 3 ---------------

        #Inlet of the Solar field
        T_in_C=sat_liq.T-273 #Same temperature than steam drum
        in_s=sat_liq.s #For plotting
        h_in=sat_liq.h #For plotting

        T_in_K=T_in_C+273
        
        # Outlet of the solar field
        x_design=0.4 #Design steam quality
        outputState=IAPWS97(P=P_op_Mpa, x=x_design)
        T_out_K=outputState.T
        T_out_C=T_out_K-273
        out_s=outputState.s
        h_out=outputState.h
        
                
    elif type_integration=="SL_S_PDS":
        
        
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
       
        x_design=0.4

        T_in_K=T_in_C+273 #Temp return of condensates
        
        initial=IAPWS97(P=P_op_Mpa, T=T_in_K)
        h_in=initial.h #kJ/kg
        in_s=initial.s
        sat_liq=IAPWS97(P=P_op_Mpa, x=0)
        outputState=IAPWS97(P=P_op_Mpa, x=x_design)
        T_out_K=outputState.T 
        T_out_C=outputState.T-273 #Temperature of saturation at that level
        
        out_s=outputState.s
        h_out=outputState.h
        
        input_ProcessState=IAPWS97(P=P_op_Mpa, x=1)
        s_process_in=input_ProcessState.s
        h_process_in=input_ProcessState.h
        
        T_avg_K=(T_in_K+T_out_K)/2
#        tempAlm=T_out_K-273
        almacenamiento=IAPWS97(P=P_op_Mpa, T=T_avg_K) #Propiedades en el almacenamiento
        almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
        almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg
        energStorageMax=almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_out_K-T_in_K)/3600 #Storage capacity in kWh
        energy_stored=0 #Initial storage
        
        #Not used
        porctSensible=0
        sat_vap=0 #Not used
        T_process_out_C=0 #Not used
        T_process_in_C=T_out_C #Not used
        T_out_HX_C=0 #Not used
        
    integrationDesign={'x_design':x_design,'porctSensible':porctSensible,'almVolumen':almVolumen,'energStorageMax':energStorageMax,
                       'T_out_process_C':T_process_in_C,'T_in_process_C':T_process_out_C,'T_out_HX_C':T_out_HX_C}
    
    mismatchDNI=0
    # --> Simulation Loop variable init
    
    theta_transv_rad=np.zeros(steps_sim)
    theta_transv_rad=theta_transv_rad
    theta_i_rad=np.zeros(steps_sim)
    theta_i_deg=np.zeros(steps_sim)
    theta_transv_deg=np.zeros(steps_sim)
    IAM_long=np.zeros(steps_sim)
    IAM_t=np.zeros(steps_sim)
    IAM=np.zeros(steps_sim)
    T_in_K=np.zeros(steps_sim)
    T_out_K=np.zeros(steps_sim)
    flowrate_kgs=np.zeros(steps_sim)
    Perd_termicas=np.zeros(steps_sim)
    flowrate_rec=np.zeros(steps_sim)
    bypass=list()
    h_in_kJkg=np.zeros(steps_sim)
    h_in_kJkg=h_in_kJkg
    Q_prod=np.zeros(steps_sim)
    Q_prod_lim=np.zeros(steps_sim)
    Q_prod_rec=np.zeros(steps_sim)
    Q_defocus=np.zeros(steps_sim)
    SOC=np.zeros(steps_sim)
    Q_charg=np.zeros(steps_sim)
    Q_discharg=np.zeros(steps_sim)
    Q_useful=np.zeros(steps_sim)
    h_out_kJkg=np.zeros(steps_sim)
    h_out_kJkg=h_out_kJkg
    flowToHx=np.zeros(steps_sim)
    flowToMix=np.zeros(steps_sim)
    flowDemand=np.zeros(steps_sim)
    T_toProcess_K=np.zeros(steps_sim)
    T_toProcess_C=np.zeros(steps_sim)
    T_alm_K=np.zeros(steps_sim)
    T_SD_K=np.zeros(steps_sim)
    storage_energy=np.zeros(steps_sim)
    SD_energy=np.zeros(steps_sim)
    x_out=np.zeros(steps_sim)
    Q_prod_steam=np.zeros(steps_sim)
    Q_drum=np.zeros(steps_sim)
    
    if sender=='CIMAV':
        blong,nlong = IAM_fiteq(type_coll,1)
        btrans,ntrans = IAM_fiteq(type_coll,2)
        lim_inf_DNI_list=[0]
    
    # BLOCK 2.2 - SIMULATION ANNUAL LOOP <><><><><><><><><><><><><><><><><><><><><><><><><><><>        
    
    # --> Instant = 0 (Initial conditions)
    bypass.append("OFF")
    Q_prod[0]=0
    T_in_K[0]=temp[0] #Ambient temperature 
    T_out_K[0]=temp[0] #Ambient temperature 
    if type_integration=="SL_S_PD":
        #Initial temperature of the steam drum
        T_SD_K[0]=T_SD_in_K #Initial temperature of the storage
        iniState=IAPWS97(P=P_op_Mpa, T=T_SD_in_K)
        SD_energy[0]=(SD_mass)*iniState.h/3600 #Storage capacity in kWh

    if type_integration=="SL_L_S" or type_integration=="SL_L_S_PH":
        T_alm_K[0]=T_ini_storage
        storage_energy[0]=storage_ini_energy
    #            SOC[i]=100*(T_alm_K[i]-273)/(T_max_storage-273)
        SOC[0]=100*energy_stored/energStorageMax

        
    for i in range(1,steps_sim): #--> <><><><>< ANNUAL SIMULATION LOOP <><><><><><><><><><><><>
           
    # --> IAM calculation
        if sender=='solatom': #Using Solatom's IAMs
            if SUN_ELV[i]>0:
                theta_transv_deg[i],theta_i_deg[i]=theta_IAMs(SUN_AZ[i],SUN_ELV[i],beta,orient_az_rad)
                theta_i_deg[i]=abs(theta_i_deg[i])
                IAM[i]=optic_efficiency_N(theta_transv_deg[i],theta_i_deg[i],n_coll_loop) #(theta_transv_deg[i],theta_i_deg[i],n_coll_loop):
            else:
                IAM_long[i]=0
                IAM_t[i]=0
                IAM[i]=IAM_long[i]*IAM_t[i]
            
        elif sender=='CIMAV': #Using CIMAV's IAMs 
            if SUN_ELV[i]>0 and SUN_ELV[i]<180:
                #calcula el angulo de incidencia transversal y longitudinal. Es decir el ángulo entre la proyeccion longitudina/tranversal y el vector area del colector
                theta_transv_deg[i],theta_i_deg[i] = theta_IAMs_CIMAV(SUN_AZ[i],SUN_ELV[i],beta,orient_az_rad,roll)
                #Dado el angulo de incidencia longitudina/transversal se calcula el IAM correspondiente con los parametros correspondientes
                IAM_long[i] = IAM_calculator(blong,nlong,theta_i_deg[i])
                IAM_t[i] = IAM_calculator(btrans,ntrans,theta_transv_deg[i])
            else:
                IAM_long[i],IAM_t[i]=0,0
            
            IAM[i]=IAM_long[i]*IAM_t[i]
            Tm_Ta=0.5*(T_in_C+T_out_C)-(temp[i]-273)#Calculates Tm-Ta in order to calculate the minimum DNI for the colector at that ambient temperature 
            lim_inf_DNI=(eta1*Tm_Ta + eta2*Tm_Ta**2)/rho_optic_0 #eta1 and eta2 are positives and the negative had to be put in the efficiency equation, from the clear of the equation rho_optic_0 is negative again and therefore everything is positive again.
            lim_inf_DNI_list+=[lim_inf_DNI]
        else:               # Using default's IAMs 
            if SUN_ELV[i]>0:
                theta_transv_deg[i],theta_i_deg[i]=theta_IAMs(SUN_AZ[i],SUN_ELV[i],beta,orient_az_rad)
                theta_i_deg[i]=abs(theta_i_deg[i])
                [IAM_long[i]]=IAM_calc(theta_i_deg[i],0,IAMfile_loc) #Longitudinal
                [IAM_t[i]]=IAM_calc(theta_transv_deg[i],1,IAMfile_loc) #Transversal
                IAM[i]=IAM_long[i]*IAM_t[i]
            else:
                IAM_long[i]=0
                IAM_t[i]=0
                IAM[i]=IAM_long[i]*IAM_t[i]
                
        
        if DNI[i]>lim_inf_DNI and SUN_ELV[i]<0: #Error in the meteo file
            mismatchDNI+=DNI[i]
            if mismatchDNI/sum(DNI)>0.02: #If the error is very low we continue with the simulation
                raise ValueError('DNI>0 when SUN_ELV<0. Check meteo file')
                
            
            
        if DNI[i]>lim_inf_DNI and SUN_ELV[i]>0 and DNI[i]>0:# Status: ON -> There's is and it is anenough DNI to start the system
            if type_integration=="SL_L_PS":
                #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 
                if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                    [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple2(simControl['itercontrol'],fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i-1],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1],sender,coll_par)
                else:
                    [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i-1],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1],sender,coll_par)
                
                [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energy_stored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageSimple(Q_prod[i],energy_stored,Demand[i],energStorageMax)     
           
            elif type_integration=="SL_L_S" or type_integration=="SL_L_S_PH":
                #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 
                
#                [T_out_K[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_kgs[i]]=operationOnlyStorageSimple(fluidInput,T_max_storage,T_alm_K[i-1],P_op_Mpa,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,flowrate_design_kgs,type_coll,sender)
                
                if (T_alm_K[i-1]+DELTA_ST)>=T_max_storage:
                    T_out_C=T_max_storage-273
                else:
                    T_out_C=(T_alm_K[i-1]+DELTA_ST-273)
                
                if type_integration=="SL_L_S":
                    
                    if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple2(simControl['itercontrol'],fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                    else:
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                if type_integration=="SL_L_S_PH":
                    T_in_C=T_alm_K[i-1]-273+DELTA_HX
                    if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple2(simControl['itercontrol'],fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                    else:
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                    
                #Storage control
                [T_alm_K[i],storage_energy[i],Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energy_stored,SOC[i],Q_defocus[i],Q_useful[i]]=outputOnlyStorageSimple(fluidInput,P_op_Mpa,T_min_storage,T_max_storage,almVolumen,T_out_K[i],T_alm_K[i-1],Q_prod[i],energy_stored,Demand[i],energStorageMax,storage_energy[i-1],storage_ini_energy,storage_min_energy,energStorageUseful,storage_max_energy)      
                
 
            elif type_integration=="SL_L_P" or type_integration=="PL_E_PM":     
                #SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
                
#                if fluidInput=="water":
#                    flowDemand[i]=Demand[i]/(h_process_in-h_process_out)#Not used, only for S_L_RF                  
#                     
#                elif fluidInput=="oil": 
#                    [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_process_K)    
#                    flowDemand[i]=Demand[i]/(Cp_av*(T_process_in_K-T_process_out_K)) #Not used, only for S_L_RF         
#                
#                elif fluidInput=="moltenSalt": 
#                    [rho_av,Cp_av,k,Dv]=moltenSalt(T_av_process_K)    
#                    flowDemand[i]=Demand[i]/(Cp_av*(T_process_in_K-T_process_out_K)) #Not used, only for S_L_RF         
#            
                if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple2(simControl['itercontrol'],fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                else:
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageSimple(Q_prod[i],Demand[i])
                                    
            elif type_integration=="SL_L_RF":
                #SL_L_RF Supply level with liquid heat transfer media return boost integration pg52
                
                if fluidInput=="water":
                    flowDemand[i]=Demand[i]/(h_process_in-h_process_out)
                    if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple2(simControl['itercontrol'],fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                    else:
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                    #Corrections in Q_prod and DEemand
                    Q_prodProcessSide=Q_prod[i]*HX_eff #Evaluation of the Energy production after the HX
                    Q_prod[i]=Q_prodProcessSide #I rename the Qprod to QprodProcessSide since this is the energy the system is transfering the process side
                    Demand_HX=Demand[i]*heatFactor #Demand of Energy at the HX
                    [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageSimple(Q_prod[i],Demand_HX)
                        
                    #HX simulation
                    if newBypass=="REC":
                        flowToHx[i]=0   #Valve closed no circulation through the HX. The solar field is recirculating
                        T_toProcess_K[i]=T_process_out_K
                        T_toProcess_C[i]=T_process_out_K-273
                    else:
                        [T_toProcess_C[i],flowToMix[i],T_toProcess_K[i],flowToMix[i],flowToHx[i]]=outputFlowsWater(Q_prod_lim[i],P_op_Mpa,h_HX_out,h_process_out,T_process_out_K,flowDemand[i])     
                else: 
                    
                    [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_process_K)    
                    flowDemand[i]=Demand[i]/(Cp_av*(T_process_in_K-T_process_out_K)) 
                    if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple2(simControl['itercontrol'],fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                    else:
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                    #Corrections in Q_prod and Demand
                    Q_prodProcessSide=Q_prod[i]*HX_eff #Evaluation of the Energy production after the HX
                    Q_prod[i]=Q_prodProcessSide #I rename the Qprod to QprodProcessSide since this is the energy the system is transfering the process side
                    Demand_HX=Demand[i]*heatFactor #Temporary correction of demand for the output function. Afterwards it is corrected again
                    [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageSimple(Q_prod[i],Demand_HX)
                        
                    
                    if newBypass=="REC":
                        flowToHx[i]=0   #Valve closed no circulation through the HX. The solar field is recirculating                         
                        T_toProcess_K[i]=T_process_out_K
                        T_toProcess_C[i]=T_process_out_K-273
                    else:
                        [T_toProcess_C[i],flowToMix[i],T_toProcess_K[i],flowToMix[i],flowToHx[i]]=outputFlowsHTF(Q_prod_lim[i],Cp_av,T_HX_out_K,T_process_out_K,flowDemand[i]) 
                                           
                  
            elif type_integration=="SL_S_FW" or type_integration=="SL_S_MW":
                #SL_S_FW Supply level with steam for solar heating of boiler feed water without storage              
                
                if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple2(simControl['itercontrol'],fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                else:
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageSimple(Q_prod[i],Demand2[i])
            
            elif type_integration=="SL_S_FWS" or type_integration=="SL_S_MWS":
                #SL_S_FW Supply level with steam for solar heating of boiler feed water with storage  
                
                if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple2(simControl['itercontrol'],fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                else:
                        [T_out_K[i],flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],theta_i_rad[i],DNI[i],IAM[i],Area,n_coll_loop,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1], sender,coll_par)
                [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energy_stored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageSimple(Q_prod[i],energy_stored,Demand2[i],energStorageMax)     
            
            elif type_integration=="SL_S_PD_OT":
                #SL_S_PD_OT Supply level with steam for direct steam generation
                if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                    [flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],x_out[i],T_out_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationDSG2(simControl['itercontrol'],bypass,bypass[i-1],T_out_K[i-1],T_in_C,P_op_Mpa,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,x_design,Q_prod_rec[i-1],subcooling)
                else:
                    [flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],x_out[i],T_out_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationDSG(bypass,bypass[i-1],T_out_K[i-1],T_in_C,P_op_Mpa,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,x_design,Q_prod_rec[i-1],subcooling)
                [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageSimple(Q_prod[i],Demand[i])
            
            elif type_integration=="SL_S_PD":
                #SL_S_PD_OT Supply level with steam for direct steam generation
                if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                    [flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],T_out_K[i],T_SD_K[i],SD_energy[i],Q_prod_steam[i]]=operationDSG_Rec2(simControl['itercontrol'],m_dot_min_kgs,bypass,SD_min_energy,T_SD_K[i-1],SD_mass,SD_energy[i-1],T_in_C,P_op_Mpa,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,x_design,PerdSD)
                else:
                    [flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],T_out_K[i],T_SD_K[i],SD_energy[i],Q_prod_steam[i]]=operationDSG_Rec(m_dot_min_kgs,bypass,SD_min_energy,T_SD_K[i-1],SD_mass,SD_energy[i-1],T_in_C,P_op_Mpa,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,x_design,PerdSD)
                [Q_prod_lim[i],Q_defocus[i],Q_useful[i],SD_energy[i],Q_prod_steam[i],Q_drum[i]]=outputDSG_Rec(SD_max_energy,SD_min_energy,SD_energy[i],SD_energy[i-1],Q_prod[i],Q_prod_steam[i],Demand[i])
            
            elif type_integration=="SL_S_PDS":
                #SL_S_PDS Supply level with steam for direct steam generation with water storage
                
                if simControl['itercontrol']=='paso_10min' or simControl['itercontrol']=='paso_15min':
                    [flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],x_out[i],T_out_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationDSG2(simControl['itercontrol'],bypass,bypass[i-1],T_out_K[i-1],T_in_C,P_op_Mpa,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,x_design,Q_prod_rec[i-1],subcooling)
                else:
                    [flowrate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],x_out[i],T_out_K[i],flowrate_rec[i],Q_prod_rec[i],newBypass]=operationDSG(bypass,bypass[i-1],T_out_K[i-1],T_in_C,P_op_Mpa,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,x_design,Q_prod_rec[i-1],subcooling)
                # [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageSimple(Q_prod[i],Demand[i])
                [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energy_stored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageSimple(Q_prod[i],energy_stored,Demand[i],energStorageMax)     
            
        
        
        else: # Status: OFF -> There's not enough DNI to put the solar plant in production     
            
            if type_integration=="SL_L_S" or type_integration=="SL_L_S_PH":
                #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 

                [T_out_K[i],Q_prod[i],T_in_K[i]]=offSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i])
#                [T_out_K[i],Q_prod[i],T_in_K[i],SOC[i],T_alm_K[i],storage_energy[i]]=offOnlyStorageSimple(T_alm_K[i-1],energStorageMax,energy_stored,T_alm_K[i-1],storage_energy[i-1],SOC[i-1]) 
                if Demand[i]>0:
                    [T_alm_K[i],storage_energy[i],Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energy_stored,SOC[i],Q_defocus[i],Q_useful[i]]=outputOnlyStorageSimple(fluidInput,P_op_Mpa,T_min_storage,T_max_storage,almVolumen,T_out_K[i],T_alm_K[i-1],Q_prod[i],energy_stored,Demand[i],energStorageMax,storage_energy[i-1],storage_ini_energy,storage_min_energy,energStorageUseful,storage_max_energy)           
                
                        
            elif type_integration=="SL_L_PS":
                #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 
                [T_out_K[i],Q_prod[i],T_in_K[i],SOC[i]]=offStorageSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i],energStorageMax,energy_stored)
                if Demand[i]>0:
                    [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energy_stored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageSimple(Q_prod[i],energy_stored,Demand[i],energStorageMax)                         
               
            elif type_integration=="SL_L_P" or type_integration=="PL_E_PM" or type_integration=="SL_L_RF":
                #SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
                
                [T_out_K[i],Q_prod[i],T_in_K[i]]=offSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i])

            elif type_integration=="SL_S_FW" or type_integration=="SL_S_MW":
                #SL_S_FW Supply level with steam for solar heating of boiler feed water without storage 
                
                [T_out_K[i],Q_prod[i],T_in_K[i]]=offSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i])
                
            elif type_integration=="SL_S_FWS" or type_integration=="SL_S_MWS":
                #SL_S_FWS Supply level with steam for solar heating of boiler feed water with storage 
                
                [T_out_K[i],Q_prod[i],T_in_K[i],SOC[i]]=offStorageSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i],energStorageMax,energy_stored)
                if Demand2[i]>0:
                    [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energy_stored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageSimple(Q_prod[i],energy_stored,Demand2[i],energStorageMax)                         
            
            elif type_integration=="SL_S_PD_OT":
                #SL_S_PD_OT Supply level with steam for direct steam generation
                [T_out_K[i],Q_prod[i],T_in_K[i]]=offSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i])
            
            elif type_integration=="SL_S_PD":
                #SL_S_PD Supply level with steam for direct steam generation
                [T_out_K[i],Q_prod[i],T_in_K[i],T_SD_K[i],SD_energy[i]]=offDSG_Rec(PerdSD,SD_limit_energy,fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i],SD_energy[i-1],SD_mass,T_SD_K[i-1],P_op_Mpa)

            elif type_integration=="SL_S_PDS":
                #SL_S_PDS Supply level with steam for direct steam generation with water storage
                [T_out_K[i],Q_prod[i],T_in_K[i],SOC[i]]=offStorageSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i],energStorageMax,energy_stored)
                if Demand[i]>0:
                    [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energy_stored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageSimple(Q_prod[i],energy_stored,Demand[i],energStorageMax)                         
               
    
    processDict={'T_in_flag':T_in_flag,'T_in_C_AR':T_in_C_AR.tolist(),'T_toProcess_C':T_toProcess_C.tolist()}
    
    # DataFRame summary of the simulation (only for SL_L_P)
#     simulationDF=pd.DataFrame({'DNI':DNI,'T_in':T_in_K-273,'T_out':T_out_K-273,'bypass':bypass,
#                               'Q_prod':Q_prod,'Q_prod_rec':Q_prod_rec,'flowrate_kgs':flowrate_kgs,
#                               'flow_rate_rec':flowrate_rec,'Q_prod_lim':Q_prod_lim,'Demand':Demand,
#                               'Q_defocus':Q_defocus})

    #DataFRame summary of the simulation (only for SL_L_S)
    simulationDF=pd.DataFrame({'DNI':DNI,'Q_prod':Q_prod,'Q_charg':Q_charg,'Q_discharg':Q_discharg,'Q_defocus':Q_defocus,'Demand':Demand,'storage_energy':storage_energy,'SOC':SOC,'T_alm_K':T_alm_K-273})
    simulationDF=simulationDF
    
    #%%
    # BLOCK 2.2 - ANUAL INTEGRATION <><><><><><><><><><><><><><><><><><><><><><><><><><><>
    
    Production_max=sum(Q_prod) #Produccion total en kWh. Asumiendo que se consume todo lo producido
    Production_lim=sum(Q_prod_lim) #Produccion limitada total en kWh
    Demand_anual=sum(Demand) #Demanda energética anual
    solar_fraction_max=100*Production_max/Demand_anual #Fracción solar maxima
    
    
    tonCo2Saved=Production_lim*co2factor #Tons of Co2 saved
    totalDischarged=(sum(Q_discharg))
#   totalCharged=(sum(Q_charg))
    Utilitation_ratio=100*((sum(Q_prod_lim))/(sum(Q_prod)))
    improvStorage=(100*sum(Q_prod_lim)/(sum(Q_prod_lim)-totalDischarged))-100 #Assuming discharged = Charged
    solar_fraction_lim=100*(sum(Q_prod_lim))/Demand_anual 
#   Energy_module_max=Production_max/num_modulos_tot
#   operation_hours=np.nonzero(Q_prod)
    if simControl['itercontrol']=='paso_10min':
        DNI_anual_irradiation=sum(DNI)/(1000*6) #kWh/year
    elif simControl['itercontrol']=='paso_15min':
        DNI_anual_irradiation=sum(DNI)/(1000*4) #kWh/year
    else:
        DNI_anual_irradiation=sum(DNI)/1000 #kWh/year
#   Optic_rho_average=(sum(IAM)*rho_optic_0)/steps_sim
    Perd_termicas=np.where(np.isnan(Perd_termicas), 0, Perd_termicas) #Avoid nan values
    Perd_term_anual=sum(Perd_termicas)/(1000) #kWh/year
    
    annualProdDict={'Q_prod':Q_prod.tolist(),'Q_prod_lim':Q_prod_lim.tolist(),'Demand':Demand.tolist(),'Q_charg':Q_charg.tolist(),
                    'Q_discharg':Q_discharg.tolist(),'Q_defocus':Q_defocus.tolist(),'solar_fraction_max':solar_fraction_max,
                    'solar_fraction_lim':solar_fraction_lim,'improvStorage':improvStorage,'Utilitation_ratio':Utilitation_ratio,
                    'flow_rate_kgs':flowrate_kgs.tolist()}
    

#%%
# ------------------------------------------------------------------------------------
# BLOCK 3 - FINANCE SIMULATION -------------------------------------------------------
# ------------------------------------------------------------------------------------
    
    Break_cost=0 # Init variable
 #   if simControl['paso_10min']==1:
  #      if finance_study==1 and steps_sim==52560:#This eneters only for yearly simulations with the flag finance_study = 1
  #  else:
    if finance_study==1 and steps_sim==8759 or steps_sim==52560 or steps_sim==35040:#This eneters only for yearly simulations with the flag finance_study = 1

    # BLOCK 3.1 - PLANT INVESTMENT <><><><><><><><><><><><><><><><><><><><><><><><><><><>

        if origin==-2: #If ReSSSPI front-end is calling, then it uses Solatom propietary cost functions
            [Selling_price,Break_cost,OM_cost_year]=SOL_plant_costFunctions(num_modulos_tot,type_integration,almVolumen,fluidInput)

        elif origin==-3: #Use the CIMAV's costs functions
            destination=[Lat,Positional_longitude]
            [Selling_price,Break_cost,OM_cost_year]=CIMAV_plant_costFunctions(num_modulos_tot,num_loops,type_integration,almVolumen,fluidInput,type_coll,destination,inputsDjango['distance']) #Returns all the prices in mxn

        else: #If othe collector is selected, it uses default cost functions
            #This function calls the standard cost functions, if necessary, please modify them within the function
            [Selling_price,Break_cost,OM_cost_year]=SP_plant_costFunctions(num_modulos_tot,type_integration,almVolumen,fluidInput)
              
        Selling_price=Selling_price*mofINV
        
    #%%    
    # BLOCK 3.2 - FINANCE MODEL <><><><><><><><><><><><><><><><><><><><><><><><><><><>
        
        if CO2==1:
            co2Savings=tonCo2Saved*co2TonPrice
        else:
            co2Savings=0
        
        # Turnkey model   
        if businessModel=="Llave en mano" or businessModel=="Turnkey project" or businessModel=="turnkey":
            [LCOE,IRR,IRR10,AmortYear,Acum_FCF,FCF,Energy_savings,OM_cost,fuelPrizeArray,Net_anual_savings]=Turn_key(Production_lim,Fuel_price,Boiler_eff,n_years_sim,Selling_price,OM_cost_year,costRaise,co2Savings)
            if lang=="spa":        
                TIRscript="TIR para el cliente"
                Amortscript="<b>Amortización: </b> Año "+ str(AmortYear)
                TIRscript10="TIR para el cliente en 10 años"
            if lang=="eng":
                TIRscript="IRR for the client"
                Amortscript="<b>Payback: </b> Year "+ str(AmortYear)
                TIRscript10="IRR for the client 10 years"
    
        
        # ESCO Energy service company model    
        if businessModel=="Compra de energia" or businessModel=="ESCO" or businessModel=="Renting":
             #From financing institution poit of view        
            [IRR,IRR10,AmortYear,Acum_FCF,FCF,BenefitESCO,OM_cost,fuelPrizeArray,Energy_savings,Net_anual_savings]=ESCO(priceReduction,Production_lim,Fuel_price,Boiler_eff,n_years_sim,Selling_price,OM_cost_year,costRaise,co2Savings)
            if lang=="spa":    
                TIRscript="TIR para la ESE"
                Amortscript="<b>Ahorro en precio actual combustible: </b>"+str(round(100*(1-priceReduction)))+"%" 
            if lang=="eng":   
                TIRscript="IRR for the ESCO"
                Amortscript="<b>Savings in fuel cost: </b>"+str(round(100*(1-priceReduction)))+"%" 
    
            #Form client point of view
            AmortYear=0
            Selling_price=0 #No existe inversión
            FCF[0]=0
            
        Energy_savingsList=[]
        OMList=[]
        fuelPrizeArrayList=[]
        Acum_FCFList=[]
        for i in range(0,len(Acum_FCF)):
            if Acum_FCF[i]<0:
                Acum_FCFList.append("("+str(int(abs(Acum_FCF[i])))+")")
            else:
                Acum_FCFList.append(str(int(Acum_FCF[i])))
        
        for i in range(0,len(fuelPrizeArray)):
            Energy_savingsList.append(round(Net_anual_savings[i]))
            OMList.append(OM_cost[i])
            fuelPrizeArrayList.append(fuelPrizeArray[i])
               
        finance={'AmortYear':AmortYear,'finance_study':finance_study,'CO2':CO2,'co2Savings':co2Savings,
                 'fuelPrizeArrayList':fuelPrizeArrayList,'Acum_FCFList':Acum_FCFList,'Energy_savingsList':Energy_savingsList,
                 'TIRscript':TIRscript,'TIRscript10':TIRscript10,'Amortscript':Amortscript,
                 'co2TonPrice':co2TonPrice,'fuelIncremento':fuelCostRaise,'IPC':CPI,'Selling_price':Selling_price,
                 'IRR':IRR,'IRR10':IRR10,'tonCo2Saved':tonCo2Saved,'OM_cost_year':OMList, 'LCOE':LCOE}
    
    else:
        n_years_sim=0 #No finance simulation
        Acum_FCF=np.array([]) #No finance simulation
        FCF=np.array([]) #No finance simulation
        AmortYear=0 #No finance simulation
        Selling_price=0 #No finance simulation
        
#%%
# ------------------------------------------------------------------------------------
# BLOCK 4 - PLOT GENERATION ----------------------------------------------------------
# ------------------------------------------------------------------------------------
    
    plotVars={'lang':lang,'Production_max':Production_max,'Production_lim':Production_lim,
              'Perd_term_anual':Perd_term_anual,'DNI_anual_irradiation':DNI_anual_irradiation,
              'Area':Area,'num_loops':num_loops,'imageQlty':imageQlty,'plotPath':plotPath,
              'Demand':Demand.tolist(),'Q_prod':Q_prod.tolist(),'Q_prod_lim':Q_prod_lim.tolist(),'type_integration':type_integration,
              'Q_charg':Q_charg.tolist(),'Q_discharg':Q_discharg.tolist(),'DNI':DNI.tolist(),'SOC':SOC.tolist(),
              'Q_useful':Q_useful.tolist(),'Q_defocus':Q_defocus.tolist(),'T_alm_K':T_alm_K.tolist(),
              'n_years_sim':n_years_sim,'Acum_FCF':Acum_FCF.tolist(),'FCF':FCF.tolist(),'m_dot_min_kgs':m_dot_min_kgs,
              'steps_sim':steps_sim,'AmortYear':AmortYear,'Selling_price':Selling_price,
              'in_s':in_s,'out_s':out_s,'T_in_flag':T_in_flag,'Fuel_price':Fuel_price,'Boiler_eff':Boiler_eff,
              'T_in_C':T_in_C,'T_in_C_AR':T_in_C_AR.tolist(),'T_out_C':T_out_C,
              'outProcess_s':s_process_in,'T_out_process_C':T_process_in_C,'P_op_bar':P_op_bar,
              'x_design':x_design,'h_in':h_in,'h_out':h_out,'hProcess_out':h_process_in,'outProcess_h':h_process_in,
              'Break_cost':Break_cost,'sender':sender,'origin':origin,
              'Q_prod_steam':Q_prod_steam.tolist(),'Q_drum':Q_drum.tolist(),'SD_min_energy':SD_min_energy,
              'SD_max_energy':SD_max_energy,'SD_energy':SD_energy.tolist()}
    
    # Plot functions

    # Plots for annual simulations
    if  steps_sim==8759:
            if plots[0]==1: #(0) Sankey plot
                image_base64,sankeyDict=SankeyPlot(sender,origin,lang,Production_max,Production_lim,Perd_term_anual,DNI_anual_irradiation,Area,num_loops,imageQlty,plotPath)
            if plots[0]==0: #(0) Sankey plot -> no plotting
                sankeyDict={'Production':0,'raw_potential':0,'Thermal_loss':0,'Utilization':0}
            if plots[1]==1: #(1) Production week Winter & Summer
                prodWinterPlot(sender,origin,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty)   
                prodSummerPlot(sender,origin,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty)  
            if plots[2]==1 and finance_study==1: #(2) Plot Finance
                financePlot(sender,origin,lang,n_years_sim,Acum_FCF,FCF,m_dot_min_kgs,steps_sim,AmortYear,Selling_price,plotPath,imageQlty)
            if plots[3]==1: #(3)Plot of Storage first week winter & summer 
               storageWinter(sender,origin,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty)    
               storageSummer(sender,origin,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty)    
            if plots[4]==1: #(4) Plot Prod months
               output_excel=prodMonths(sender,origin,Q_prod,Q_prod_lim,DNI,Demand,lang,plotPath,imageQlty)
               output_excel=output_excel
            if plots[15]==1: #(15) Plot Month savings
               output_excel2=savingsMonths(sender,origin,Q_prod_lim,Energy_Before,Fuel_price,Boiler_eff,lang,plotPath,imageQlty)
               output_excel2=output_excel2
    elif steps_sim==52560 or steps_sim==35040:
            if plots[0]==1: #(0) Sankey plot
                image_base64,sankeyDict=SankeyPlot(sender,origin,lang,Production_max,Production_lim,Perd_term_anual,DNI_anual_irradiation,Area,num_loops,imageQlty,plotPath)
            if plots[0]==0: #(0) Sankey plot -> no plotting
                sankeyDict={'Production':0,'raw_potential':0,'Thermal_loss':0,'Utilization':0}
            if plots[1]==1: #(1) Production week Winter & Summer
                prodWinterPlot2(simControl['itercontrol'],sender,origin,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty)   
                prodSummerPlot2(simControl['itercontrol'],sender,origin,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty)  
            if plots[2]==1 and finance_study==1: #(2) Plot Finance
                financePlot(sender,origin,lang,n_years_sim,Acum_FCF,FCF,m_dot_min_kgs,steps_sim,AmortYear,Selling_price,plotPath,imageQlty)
            if plots[3]==1: #(3)Plot of Storage first week winter & summer 
               storageWinter2(simControl['itercontrol'],sender,origin,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty)    
               storageSummer2(simControl['itercontrol'],sender,origin,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty)    
            if plots[4]==1: #(4) Plot Prod months
               output_excel=prodMonths2(simControl['itercontrol'],sender,origin,Q_prod,Q_prod_lim,DNI,Demand,lang,plotPath,imageQlty)
               output_excel=output_excel
            if plots[15]==1: #(15) Plot Month savings
               output_excel2=savingsMonths2(simControl['itercontrol'],sender,origin,Q_prod_lim,Energy_Before,Fuel_price,Boiler_eff,lang,plotPath,imageQlty)
               output_excel2=output_excel2
    
    # Plots for non-annual simulatios (With annual simuations you cannot see anything)
    
    if steps_sim!=8759 and steps_sim!=52560 and steps_sim!=35040:
        if simControl['itercontrol']=='paso_10min'or simControl['itercontrol']=='paso_15min':
            if plots[5]==1: #(5) Theta angle Plot
                thetaAnglesPlot2(simControl['itercontrol'],sender,origin,step_sim,steps_sim,theta_i_deg,theta_transv_deg,plotPath,imageQlty)
            if plots[6]==1: #(6) IAM angles Plot
                IAMAnglesPlot2(simControl['itercontrol'],sender,origin,step_sim,IAM_long,IAM_t,IAM,plotPath,imageQlty) 
            if plots[7]==1: #(7) Plot Overview (Demand vs Solar Radiation) 
                demandVsRadiation2(simControl['itercontrol'],sender,origin,lang,step_sim,Demand,Q_prod,Q_prod_lim,Q_prod_rec,steps_sim,DNI,plotPath,imageQlty)
            if plots[8]==1: #(8) Plot flowrates  & Temp & Prod
                flowRatesPlot2(simControl['itercontrol'],sender,origin,step_sim,steps_sim,flowrate_kgs,flowrate_rec,num_loops,flowDemand,flowToHx,flowToMix,m_dot_min_kgs,T_in_K,T_toProcess_C,T_out_K,T_alm_K,plotPath,imageQlty)
            if plots[9]==1: #(9)Plot Storage non-annual simulation  
                storageNonAnnual2(simControl['itercontrol'],sender,origin,SOC,Q_useful,Q_prod,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty)
            if plots[16]==1 and type_integration=='SL_S_PD': #(16)Plot for SL_S_PD
                SL_S_PDR_Plot2(simControl['itercontrol'],sender,origin,step_sim,steps_sim,SD_min_energy,SD_max_energy,Q_prod,Q_prod_steam,SD_energy,T_in_K,T_out_K,T_SD_K,plotPath,imageQlty)
            if plots[17]==1 and type_integration=='SL_S_PD': #(17)Plot for SL_S_PD 
                storageNonAnnualSL_S_PDR2(simControl['itercontrol'],sender,origin,SOC,Q_useful,Q_prod_steam,Q_prod,Q_drum,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty)
        else:
            if plots[5]==1: #(5) Theta angle Plot
                thetaAnglesPlot(sender,origin,step_sim,steps_sim,theta_i_deg,theta_transv_deg,plotPath,imageQlty)
            if plots[6]==1: #(6) IAM angles Plot
                IAMAnglesPlot(sender,origin,step_sim,IAM_long,IAM_t,IAM,plotPath,imageQlty) 
            if plots[7]==1: #(7) Plot Overview (Demand vs Solar Radiation) 
                demandVsRadiation(sender,origin,lang,step_sim,Demand,Q_prod,Q_prod_lim,Q_prod_rec,steps_sim,DNI,plotPath,imageQlty)
            if plots[8]==1: #(8) Plot flowrates  & Temp & Prod
                flowRatesPlot(sender,origin,step_sim,steps_sim,flowrate_kgs,flowrate_rec,num_loops,flowDemand,flowToHx,flowToMix,m_dot_min_kgs,T_in_K,T_toProcess_C,T_out_K,T_alm_K,plotPath,imageQlty)
            if plots[9]==1: #(9)Plot Storage non-annual simulation  
                storageNonAnnual(sender,origin,SOC,Q_useful,Q_prod,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty)
            if plots[16]==1 and type_integration=='SL_S_PD': #(16)Plot for SL_S_PD
                SL_S_PDR_Plot(sender,origin,step_sim,steps_sim,SD_min_energy,SD_max_energy,Q_prod,Q_prod_steam,SD_energy,T_in_K,T_out_K,T_SD_K,plotPath,imageQlty)
            if plots[17]==1 and type_integration=='SL_S_PD': #(17)Plot for SL_S_PD 
                storageNonAnnualSL_S_PDR(sender,origin,SOC,Q_useful,Q_prod_steam,Q_prod,Q_drum,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty)
    # Property plots
    if fluidInput=="water" or fluidInput=="steam": #WATER or STEAM
        if plots[10]==1: #(10) Mollier Plot for s-t for Water
            mollierPlotST(sender,origin,lang,type_integration,in_s,out_s,T_in_flag,T_in_C,T_in_C_AR,T_out_C,s_process_in,T_process_in_C,P_op_bar,x_design,plotPath,imageQlty)              
        if plots[11]==1: #(11) Mollier Plot for s-h for Water 
            mollierPlotSH(sender,origin,lang,type_integration,h_in,h_out,h_process_in,h_process_in,in_s,out_s,T_in_flag,T_in_C,T_in_C_AR,T_out_C,s_process_in,T_process_in_C,P_op_bar,x_design,plotPath,imageQlty)  
    if fluidInput=="oil": 
        if plots[12]==1:
            rhoTempPlotOil(sender,origin,lang,T_out_C,plotPath,imageQlty) #(12) Plot thermal oil properties Rho & Cp vs Temp
        if plots[13]==1:
            viscTempPlotOil(sender,origin,lang,T_out_C,plotPath,imageQlty) #(13) Plot thermal oil properties Viscosities vs Temp        
    if fluidInput=="moltenSalt": 
        if plots[12]==1:
            rhoTempPlotSalt(sender,origin,lang,T_out_C,plotPath,imageQlty) #(12) Plot thermal oil properties Rho & Cp vs Temp
        if plots[13]==1:
            viscTempPlotSalt(sender,origin,lang,T_out_C,plotPath,imageQlty) #(13) Plot thermal oil properties Viscosities vs Temp        


    
    # Other plots
    if plots[14]==1: #(14) Plot Production
        if simControl['itercontrol']=='paso_10min'or simControl['itercontrol']=='paso_15min':
            productionSolar2(simControl['itercontrol'],sender,origin,lang,step_sim,DNI,m_dot_min_kgs,steps_sim,Demand,Q_prod,Q_prod_lim,Q_charg,Q_discharg,type_integration,plotPath,imageQlty)
        else:
           productionSolar(sender,origin,lang,step_sim,DNI,m_dot_min_kgs,steps_sim,Demand,Q_prod,Q_prod_lim,Q_charg,Q_discharg,type_integration,plotPath,imageQlty)
    
#%%
# ------------------------------------------------------------------------------------
# BLOCK 5 - REPORT GENERATION ----------------------------------------------------------
# ------------------------------------------------------------------------------------
    
    # Create Report with results (www.ressspi.com uses a customized TEMPLATE called in the function "reportOutput"
    if steps_sim==8759 or steps_sim==52560 or steps_sim==35040: #The report is only available when annual simulation is performed
        if origin==-2:
            fileName="results"+str(pk)
            reportsVar={'logo_output':'no_logo','date':inputs['date'],'type_integration':type_integration,
                        'fileName':fileName,'reg':pk,
                        'Area_total':Area_total,'n_coll_loop':n_coll_loop,
                        'num_loops':num_loops,'m_dot_min_kgs':m_dot_min_kgs}



            
            reportsVar.update(inputs)
            reportsVar.update(finance)
            reportsVar.update(confReport)
            reportsVar.update(annualProdDict)
            reportsVar.update(sankeyDict)
            reportsVar.update(meteoDict)
            reportsVar.update(processDict)
            reportsVar.update(integrationDesign)   
            template_vars=reportOutput(origin,reportsVar,-1,"",pk,version,os.path.dirname(os.path.dirname(__file__))+'/ressspi',os.path.dirname(os.path.dirname(__file__)),Energy_Before_annual,sankeyDict)
        
        else:
            template_vars={} 
            reportsVar={'version':version,'logo_output':'no_logo','version':version,'type_integration':type_integration,
                        'energyStored':energy_stored,"location":localMeteo,
                        'Area_total':Area_total,'n_coll_loop':n_coll_loop,
                        'num_loops':num_loops,'m_dot_min_kgs':m_dot_min_kgs,
                        'Production_max':Production_max,'Production_lim':Production_lim,
                        'Demand_anual':Demand_anual,'solar_fraction_max':solar_fraction_max,
                        'solar_fraction_lim':solar_fraction_lim,'DNI_anual_irradiation':DNI_anual_irradiation}
            reportsVar.update(finance)
            reportsVar.update(confReport)
            reportsVar.update(annualProdDict)
            reportsVar.update(modificators)
            if origin==0 or origin == -3:
                reportOutputOffline(reportsVar)
    else:
        template_vars={}
        reportsVar={}
        
    return(template_vars,plotVars,reportsVar,version)


# ----------------------------------- END SHIPcal -------------------------
# -------------------------------------------------------------------------
#%% 
'''
# Variables needed for calling SHIPcal from terminal
    
#Plot Control ---------------------------------------
imageQlty=200

plots=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1] # Put 1 in the elements you want to plot. Example [1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0] will plot only plots #0, #8 and #9
#(0) A- Sankey plot
#(1) A- Production week Winter & Summer
#(2) A- Plot Finance
#(3) A- Plot of Storage first week winter & summer
#(4) A- Plot Prod months
#(5) NA- Theta angle Plot
#(6) NA- IAM angles Plot
#(7) NA- Plot Overview (Demand vs Solar Radiation)
#(8) NA- Plot flowrates  & Temp & Prod
#(9) NA- Plot Storage non-annual simulation 
#(10) P- Mollier Plot for s-t for Water
#(11) P- Mollier Plot for s-h for Water
#(12) P- Plot thermal oil/molten salt properties Rho & Cp vs Temp
#(13) P- Plot thermal oil/molten salt properties Viscosities vs Temp 
#(14) Plot Production 
#(15) A- Plot Month savings 
#(16) NA- Plot for SL_S_PD



finance_study=1

#iteration´s variable of control

#paso_10min
#paso_15min
itercontrol ='paso_10min'
#In case the TMY does not have solar time. Equations implemented in SolarEQ_simple2
to_solartime='on' # value must be on to use.
huso=0 #UTC. This value correspond to the time zone of the hour in the TMY.

month_ini_sim=5
day_ini_sim=1
hour_ini_sim=24 #--->For ten minutes or fifteen minutes simulations, day starts at 0 hours and ends at 24 hours
ten_min_ini_sim=0 # 0 to 5--->{0=0 min; 1=10 min; 2=20 min; 3=30 min; 4=40 min; 5= 50 min}
fifteen_min_ini_sim=0 # 0 to 3--->{0=0 min; 1=15 min; 2=30 min; 3=45}

month_fin_sim=5
day_fin_sim=2
hour_fin_sim=16 #--->For ten minutes or fifteen minutes simulations, day starts at 0 hours and ends at 24 hours
ten_min_fin_sim=2 #0 to 5--->{0=0 min; 1=10 min; 2=20 min; 3=30 min; 4=40 min; 5= 50 min}
fifteen_min_fin_sim=3 # 0 to 3--->{0=0 min; 1=15 min; 2=30 min; 3=45 min}









# -------------------- FINE TUNNING CONTROL ---------
mofINV=1 #Sobre el coste de inversion
mofDNI=1  #Corrección a fichero Meteonorm
mofProd=1 #Factor de seguridad a la producción de los módulos

# -------------------- SIZE OF THE PLANT ---------
num_loops=4
n_coll_loop=8


#SL_L_P -> Supply level liquid parallel integration without storage
#SL_L_PS -> Supply level liquid parallel integration with storage
#SL_L_RF -> Supply level liquid return flow boost
#SL_L_DRF -> Supply level liquid return flow boost with no heat exchanger (The simplest)
#SL_L_S -> Storage
#SL_L_S_PH -> Storage preheat
#SL_S_FW -> Supply level solar steam for heating of boiler feed water without storage
#SL_S_FWS -> Supply level solar steam for heating of boiler feed water with storage
#SL_S_PD_OT -> Supply level solar steam for direct solar steam generation #For CIMAV only works for a large number of plane collectors +30
#PL_E_PM ->
#SL_S_MW ->
#SL_S_MWS ->
#SL_S_PD ->
#SL_S_PDS -> #For CIMAV only works for a large number of plane collectors +20

type_integration="SL_S_PD" 
almVolumen=10000 #litros

# --------------------------------------------------
confReport={'lang':'spa','sender':'sevilla','cabecera':'Resultados de la <br> simulación','mapama':0}
modificators={'mofINV':mofINV,'mofDNI':mofDNI,'mofProd':mofProd}
desginDict={'num_loops':num_loops,'n_coll_loop':n_coll_loop,'type_integration':type_integration,'almVolumen':almVolumen}
simControl={'finance_study':finance_study,'mes_ini_sim':month_ini_sim,'dia_ini_sim':day_ini_sim,'hora_ini_sim':hour_ini_sim,'mes_fin_sim':month_fin_sim,'dia_fin_sim':day_fin_sim,'hora_fin_sim':hour_fin_sim, 'itercontrol':itercontrol,'to_solartime':to_solartime,'huso':huso}    
if itercontrol =='paso_10min':
    simControl={'finance_study':finance_study,'mes_ini_sim':month_ini_sim,'dia_ini_sim':day_ini_sim,'hora_ini_sim':hour_ini_sim,'mes_fin_sim':month_fin_sim,'dia_fin_sim':day_fin_sim,'hora_fin_sim':hour_fin_sim, 'itercontrol':itercontrol,'ten_min_ini_sim':ten_min_ini_sim, 'ten_min_fin_sim':ten_min_fin_sim,'to_solartime':to_solartime, 'huso':huso}
elif itercontrol =='paso_15min':
    simControl={'finance_study':finance_study,'mes_ini_sim':month_ini_sim,'dia_ini_sim':day_ini_sim,'hora_ini_sim':hour_ini_sim,'mes_fin_sim':month_fin_sim,'dia_fin_sim':day_fin_sim,'hora_fin_sim':hour_fin_sim, 'itercontrol':itercontrol,'fifteen_min_ini_sim':fifteen_min_ini_sim, 'fifteen_min_fin_sim':fifteen_min_fin_sim,'to_solartime':to_solartime, 'huso':huso}
# ---------------------------------------------------

origin=1 #0 if new record; -2 if it comes from www.ressspi.com

if origin==0:
    #To perform simulations from command line using hardcoded inputs
    inputsDjango={}
    last_reg=666
elif origin==-3:
    inputsDjango= 	{'T_in_flag': 1,
                     'businessModel': 'turnkey',
                     'co2TonPrice': 0.0,
                     'co2factor': 0.0,
                     'collector_type': 'BOSCH SKW2.txt',
                     'date': 'hoy',
                     'demand': 6000.0,
                     'demandUnit': '666',
                     'email': 'ja.arpa97@gmail.com',
                     'every_day': True,
                     'every_month': True,
                     'fluid': 'water',
                     'fuel': 'gas_licuado_petroleo',
                     'fuelPrice': 1.089539826506024,
                     'fuelUnit': 1.0,
                     'hourEND': 17,
                     'hourINI': 9,
                     'industry': 'Secado de Chiles',
                     'location': 'Zacatecas.dat',
                     'name': '',
                     'pais': 'México',
                     'pressure': 1.0,
                     'pressureUnit': '1',
                     'semana': ['0', '1', '2', '3', '4', '5', '6'],
                     'surface': 150.0,
                     'tempIN': 23.0,
                     'tempOUT': 50.0,
                     'year': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']}
    last_reg=666
    
else:
    #To perform simulations from command line using inputs like if they were from django
    # inputsDjango={'pressureUnit':'bar',
    #               'pressure':30,
    #               'demand':1875*8760,
    #               'demandUnit':'kWh',
    #               'hourEND':24,
    #               'hourINI':1,
    #               'Jan':1/12,
    #               'Feb':1/12,
    #               'Mar':1/12,
    #               'Apr':1/12,
    #               'May':1/12,
    #               'Jun':1/12,
    #               'Jul':1/12,
    #               'Aug':1/12,
    #               'Sep':1/12,
    #               'Oct':1/12,
    #               'Nov':1/12,
    #               'Dec':1/12,
    #               'Mond':0.143,
    #               'Tues':0.143,
    #               'Wend':0.143,
    #               'Thur':0.143,
    #               'Fri':0.143,
    #               'Sat':0.143,
    #               'Sun':0.143,
    #               'date':'2020-05-08',
    #               'name':'jaarpa',
    #               'industry':'comparison_test',
    #               'email':'jaarpa97@gmail.com',
    #               'sectorIndustry':'developing',
    #               'fuel':'Gasoil-B',
    #               'fuelPrice':0.05,
    #               'co2TonPrice':0,
    #               'co2factor':1,
    #               'fuelUnit':'kWh',
    #               'businessModel':'turnkey',
    #               'location':'Bakersfield',
    #               'location_aux':'',
    #               'surface':None,
    #               'terrain':'',
    #               'orientation':'NS',
    #               'inclination':'flat',
    #               'shadows':'free',
    #               'distance':None,
    #               'process':'',
    #               'fluid':'steam',
    #               'connection':'',
    #               'tempOUT':235,
    #               'tempIN':20,
    #               'last_reg':666
    #              }
    
    last_reg=666
    inputsDjango= {'date': '2020-07-06', 'name': 'miguel', 'email': 'miguel.frasquet@solatom.com', 'industry': 'seminario', 'sectorIndustry': 'Agro_Livestock', 'fuel': 'NG', 'fuelPrice': 0.05, 'co2TonPrice': 0.0, 'co2factor': 0.0002, 'fuelUnit': 'eur_kWh', 'businessModel': 'turnkey', 'location': 'Albuquerque', 'location_aux': '', 'surface': None, 'terrain': '', 'distance': None, 'orientation': 'NS', 'inclination': 'flat', 'shadows': 'free', 'fluid': 'steam', 'pressure': 6.0, 'pressureUnit': 'bar', 'tempIN': 80.0, 'tempOUT': 135.0, 'connection': '', 'process': '', 'demand': 7884.0, 'demandUnit': 'MWh', 'hourINI': 1, 'hourEND': 24, 'Mond': 0.143, 'Tues': 0.143, 'Wend': 0.143, 'Thur': 0.143, 'Fri': 0.143, 'Sat': 0.143, 'Sun': 0.143, 'Jan': 0.083, 'Feb': 0.083, 'Mar': 0.083, 'Apr': 0.083, 'May': 0.083, 'Jun': 0.083, 'Jul': 0.083, 'Aug': 0.083, 'Sep': 0.083, 'Oct': 0.083, 'Nov': 0.083, 'Dec': 0.083, 'last_reg': 772}
    #last_reg=inputsDjango['last_reg']
    
[jSonResults,plotVars,reportsVar,version]=SHIPcal(origin,inputsDjango,plots,imageQlty,confReport,modificators,desginDict,simControl,last_reg)
'''
