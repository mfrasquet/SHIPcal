#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 12:19:06 2018

@author: miguel
"""
import sys
sys.path.append('General_modules')

from General_modules.func_General import annualConsumpFromRessspi



def djangoReport(inputsDjango):
#    if inputsDjango['location']=="" and inputsDjango['location']!="":
#        inputsDjango['location']=inputsDjango['location']
#    
#    if inputsDjango['location']!="" and inputsDjango['location']!="":
#        inputsDjango['location']=inputsDjango['location']
    
    if inputsDjango['pressureUnit']=='bar':
        factor_uni_pressure=1
    if inputsDjango['pressureUnit']=='MPa':
        factor_uni_pressure=10
    if inputsDjango['pressureUnit']=='psi':
        factor_uni_pressure=0.068948
    
    P_op_bar=inputsDjango['pressure']*factor_uni_pressure #Correcion de presion por unidades
    
    
    #Energy calculations for graphs
    
    annualConsumption=inputsDjango['demand']
    
    #definicion unidades de energia
    if inputsDjango['demandUnit']=='kWh':
        factor_uni_consum=1/1000
    if inputsDjango['demandUnit']=='MWh':
        factor_uni_consum=1000/1000
    if inputsDjango['demandUnit']=='GWh':
        factor_uni_consum=1000000/1000
    if inputsDjango['demandUnit']=='KJ':
        factor_uni_consum=0.000278/1000
    if inputsDjango['demandUnit']=='BTU':
        factor_uni_consum=0.000293/1000
    if inputsDjango['demandUnit']=='kcal':
        factor_uni_consum=0.001162/1000
        
    annualConsumption=annualConsumption*factor_uni_consum
    annualConsumptionkWh=annualConsumption*1000
    
   
    dayArray=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    activeHours=int(inputsDjango['hourEND'])-int(inputsDjango['hourINI'])
    porctDay=1/activeHours
    for j in range(int(inputsDjango['hourINI'])-1,int(inputsDjango['hourEND'])):
        dayArray[j]=porctDay
 
    
    monthArray=[inputsDjango['Jan'],inputsDjango['Feb'],inputsDjango['Mar'],inputsDjango['Apr'],inputsDjango['May'],inputsDjango['Jun'],inputsDjango['Jul'],inputsDjango['Aug'],inputsDjango['Sep'],inputsDjango['Oct'],inputsDjango['Nov'],inputsDjango['Dec']]
    weekArray=[inputsDjango['Mond'],inputsDjango['Tues'],inputsDjango['Wend'],inputsDjango['Thur'],inputsDjango['Fri'],inputsDjango['Sat'],inputsDjango['Sun']]
    
    inputs = {"date":inputsDjango['date'], "nameUser" :inputsDjango['name'],"companyName": inputsDjango['industry'],
            "emailUser" :inputsDjango['email'],"sectorUser":inputsDjango['sectorIndustry'],
            "currentFuel":inputsDjango['fuel'],"fuelPrice":inputsDjango['fuelPrice'],
            "co2TonPrice":inputsDjango['co2TonPrice'],
            "co2factor":inputsDjango['co2factor'],
            "priceUnit":inputsDjango['fuelUnit'],
            "businessModel":inputsDjango['businessModel'],
            "location":inputsDjango['location'],"surfaceAvailable":inputsDjango['surface'],
            "terrainType": inputsDjango['terrain'],
            "orientation":inputsDjango['orientation'],
            "inclination":inputsDjango['inclination'],
            "shadow":inputsDjango['shadows'],
            "distance":inputsDjango['distance'],
            "mainProcess":inputsDjango['process'],
            "fluid":inputsDjango['fluid'],
            "pressure":inputsDjango['pressure'],
            "pressureUnit":inputsDjango['pressureUnit'],
            "connectProcess":inputsDjango['connection'],
            "outletTemp":inputsDjango['tempOUT'],
            "inletTemp":inputsDjango['tempIN'],
            "energyConsumption":inputsDjango['demand'],
            "energyConsumptionUnits":inputsDjango['demandUnit'],
            "typeProcessDay":'',
            "dayProfile":'',
            "weekProfile":'',         
            "annualProfile":'',
            'localInput':''}

    return (inputs,annualConsumptionkWh,inputsDjango['last_reg'],P_op_bar,monthArray,weekArray,dayArray)

#inputsDjango={'date': '2018-08-04', 'name': 'miguel', 'email': 'miguel.frasquet@solatom.com', 'industry': 'miguel', 'sectorIndustry': 'Minning', 'fuel': 'LNG', 'fuelPrice': 0.07, 'fuelUnit': 'eur_kWh', 'businessModel': 'turnkey', 'location': 'Almeria', 'location_aux': '', 'surface': 2000, 'terrain': 'clean_ground', 'distance': 2000, 'orientation': 'NS', 'inclination': 'flat', 'shadows': 'free', 'fluid': 'steam', 'pressure': 10.0, 'pressureUnit': 'bar', 'tempIN': 100.0, 'tempOUT': 184.0, 'connection': 'process', 'process': '', 'demand': 5000.0, 'demandUnit': 'MWh', 'hourINI': '1', 'hourEND': '24', 'Mond': 0.16666666666666666, 'Tues': 0.16666666666666666, 'Wend': 0.16666666666666666, 'Thur': 0.16666666666666666, 'Fri': 0.2, 'Sat': 0.0, 'Sun': 0.0, 'Jan': 0.09090909090909091, 'Feb': 0.09090909090909091, 'Mar': 0.09090909090909091, 'Apr': 0.09090909090909091, 'May': 0.09090909090909091, 'Jun': 0.09090909090909091, 'Jul': 0.09090909090909091, 'Aug': 0.09090909090909091, 'Sep': 0.0, 'Oct': 0.09090909090909091, 'Nov': 0.09, 'Dec': 0.09, 'last_reg': 80}

#
#(inputs,annualConsumptionkWh,last_reg,P_op_bar,activeMonthsArray,activeWeekArray,activeHoursArray)=djangoReport(inputsDjango)
    


