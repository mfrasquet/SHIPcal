#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 19:54:51 2016

@author: Miguel Frasquet
"""

#Standard Libs
import sys
import os
import numpy as np
import pandas as pd
import datetime
from iapws import IAPWS97

#Place to import customized Libs
sys.path.append(os.path.dirname(os.path.dirname(__file__))+'/ressspi_solatom/') #SOLATOM
from Solatom_modules.Solatom_finance import Turn_key,ESCO
from Solatom_modules.Solatom_finance import SP_plant_bymargin,SP_plant_bymargin2
from Solatom_modules.templateSolatom import reportOutput
from Solatom_modules.solatom_param import solatom_param

#Place to import Ressspi Libs

from General_modules.func_General import bar_MPa,MPa_bar,C_K,K_C,check_overwrite,DemandData,waterFromGrid,thermalOil,reportOutputOffline 
from General_modules.demandCreator_v1 import demandCreator
from General_modules.fromDjangotoRessspi import djangoReport
from Solar_modules.EQSolares import SolarData
from Solar_modules.EQSolares import theta_IAMs
from Solar_modules.EQSolares import IAM_calc
from Solar_modules.iteration_process import flow_calc, flow_calcOil
from Solar_modules.iteration_process import IT_temp,IT_tempOil
from Integration_modules.integrations import *
from Plot_modules.plottingRessspi import *


def ressspiSIM(ressspiReg,inputsDjango,plots,imageQlty,confReport,modificators,desginDict,simControl,pk):
    #%%
    
   
    #Sender identity. Needed for use customized modules or generic modules (Solar collectors, finance, etc.)
    sender=confReport['sender']
    
    version="1.0.7" #Ressspi version
    lang=confReport['lang'] #Language
        
    #Paths
    if ressspiReg==-2:
        plotPath=os.path.dirname(os.path.dirname(__file__))+'/ressspi/ressspiForm/static/results/' #FilePath for images when called by www.ressspi.com
    if ressspiReg==0:
        plotPath=""
    
    
    #Input Control ---------------------------------------
    
    mofINV=modificators['mofINV']
    mofDNI=modificators['mofDNI']
    mofProd=modificators['mofProd']
    

    num_loops=desginDict['num_loops']
    n_coll_loop=desginDict['n_coll_loop']
    type_integration=desginDict['type_integration']
    almVolumen=0 #litres   
    almVolumen=desginDict['almVolumen']
    
    #Simulation Control ---------------------------------------
    finance_study=simControl['finance_study']
    
    mes_ini_sim=simControl['mes_ini_sim']
    dia_ini_sim=simControl['dia_ini_sim']
    hora_ini_sim=simControl['hora_ini_sim']
    
    mes_fin_sim=simControl['mes_fin_sim'] 
    dia_fin_sim=simControl['dia_fin_sim']
    hora_fin_sim=simControl['hora_fin_sim']
    
   
    #%%
    # ------------------------------------- INPUTS --------------------------------
    
    if ressspiReg==-2: #Simulation called from frontend -> www.ressspi.com
             
        ## ENERGY DEMAND
        [inputs,annualConsumptionkWh,reg,P_op_bar,monthArray,weekArray,dayArray]=djangoReport(inputsDjango)
        file_demand=demandCreator(annualConsumptionkWh,dayArray,weekArray,monthArray)
       
        annualConsumptionkWh=annualConsumptionkWh
        arraysConsumption={'dayArray':dayArray,'weekArray':weekArray,'monthArray':monthArray}
        inputs.update(arraysConsumption)
        
        ## PROCESS
        fluidInput=inputs['fluid'] #Type of fluid 
        T_out_C=inputs['outletTemp'] #Temperatura alta
        T_in_C=inputs['inletTemp'] #Temperatura baja
        P_op_bar=P_op_bar
            
        ## FINANCE
        businessModel=inputs['businessModel'] 
        fuel=inputs['currentFuel']
        Fuel_price=inputs['fuelPrice']   #Price of fossil fuel in €/kWh
        co2TonPrice=inputs['co2TonPrice']
        co2factor=inputs['co2factor']
         
        ## METEO
        meteoDB = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/meteoDB.csv", sep=',') 
        locationFromRessspi=inputs['location']
        localMeteo=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'meteoFile'].iloc[0]
        file_loc=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/"+localMeteo 
        Lat=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'Latitud'].iloc[0]
        Huso=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'Huso'].iloc[0]
        
                  
    if ressspiReg==0:  #Simulation called from Python file

        ## TO BE IMPLEMENTED 
        surfaceAvailable=1000 #Surface available for the solar plant
        orientation="NS" 
        inclination="flat"
        shadowInput="free"
        distanceInput=15 #From the solar plant to the network integration point (in meters)
        terreno="clean_ground"
        
        ## ENERGY DEMAND
        dayArray=[0,0,0,0,0,0,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,0,0,0,0,0,0] #12 hours day profile
        weekArray=[0.2,0.2,0.2,0.2,0.2,0,0] #No weekends
        monthArray=[1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12] #Whole year     
        totalConsumption=190000 #kWh
        file_demand=demandCreator(totalConsumption,dayArray,weekArray,monthArray)
        
        ## PROCESS
        fluidInput="steam" #"Agua sobrecalentada" "vapor" "Aceite térmico" 
        T_out_C=180 #Temperatura alta
        T_in_C=90 #Temperatura baja
        P_op_bar=8 #bar 
        
        ## FINANCE
        businessModel="turnkey"
        fuel="Gasoil-B" #Type of fuel
        Fuel_price=0.05 #Price of fossil fuel in €/kWh
        co2TonPrice=7.5 #(€/TonCo2)
        co2factor=1 #Default value 1, after it will be modified

        ## METEO
        localMeteo="Badajoz.dat" #Be sure this location is included in Ressspi DB
        meteoDB = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/meteoDB.csv", sep=',') 
        file_loc=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/"+localMeteo       
        Lat=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Latitud'].iloc[0]
        Huso=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Huso'].iloc[0]
        
        # -------------------------------------------------
        
        
        if fuel in ["NG","LNG"]:
            co2factor=.2/1000 #TonCo2/kWh  #https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html
        if fuel in ['Fueloil2','Fueloil3','Gasoil-B','Gasoil-C']:
            co2factor=.27/1000 #TonCo2/kWh       #https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html    
        if fuel in ['Electricity']:
            co2factor=.385/1000 #TonCo2/kWh  #https://www.eia.gov/tools/faqs/faq.php?id=74&t=11
        if fuel in ['Propane','Butane','Air-propane']:
            co2factor=.22/1000 #TonCo2/kWh    #https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html  
        if fuel in ['Biomass']:
            co2factor=.41/1000 #TonCo2/kWh  #https://www.engineeringtoolbox.com/co2-emission-fuels-d_1085.html

        # --------------------------------------------------------------------------------------

    
    #%%
    

        
    # -----------------------------------------------
    
    #Collector
    if sender=='solatom': #Using Solatom Collector
        type_coll=20 #Solatom 20" fresnel collector - Change if other collector is used
        IAM_file='Solatom.csv'
        IAM_folder=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/IAM_files/"
        REC_type=1
        
    else: #Using other collectors (to be filled with customized data)
        #CAMBIAR !!!!
        type_coll=20 #Solatom 20" fresnel collector - Change if other collector is used
        IAM_file='Solatom.csv'
        IAM_folder=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/IAM_files/"
        REC_type=1
        
    IAMfile_loc=IAM_folder+IAM_file
    beta=0 #Inclination not implemented
    orient_az_rad=0 #Orientation not implemented
       
    
    D,Area_coll,rho_optic_0,huella_coll,Long,Apert_coll=solatom_param(type_coll)
    Area=Area_coll*n_coll_loop #Area of one loop
    Area_total=Area*num_loops #Total area
    
    #Process control
    T_in_C_AR_mes=np.array([8,9,11,13,14,15,16,15,14,13,11,8]) #When input process is water from the grid. Ressspi needs the monthly average temp of the water grid
    T_in_C_AR=waterFromGrid(T_in_C_AR_mes)
    #Process parameters
    lim_inf_DNI=200 #Minimum temperature to start production
    m_dot_min_kgs=0.08 #Minimum flowrate before re-circulation
    coef_flow_rec=2 #Multiplier for flowrate when recirculating
    
    
    
    # ---------------------------------------------------------------------
    # --------------------------- SIMULATION ------------------------------
    # ---------------------------------------------------------------------
      
        
    num_modulos_tot=n_coll_loop*num_loops
    
    #Solar Data
    output,hour_year_ini,hour_year_fin=SolarData(file_loc,Lat,Huso,mes_ini_sim,dia_ini_sim,hora_ini_sim,mes_fin_sim,dia_fin_sim,hora_fin_sim)
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
            
    """
    T_in_flag=1 #Flag 1 si la temperatura es constante (circuito cerrado); 0 si se toma agua de red (circuito abierto con reposicion)
    
    #Renombramos variables y las transformamos para trabajar mas comodo
    month=output[:,0]
    day_month=output[:,1]
    hour_day=output[:,2]
    hour_year= output[:,3]
    #W=output[:,4]
    SUN_ELV=output[:,5] #rad
    SUN_AZ=output[:,6] #rad
    #DECL=output[:,7] - #rad
    #SUN_ZEN=output[:,8] #rad
    DNI=output[:,9] *mofDNI # W/m2
    DNI_positive_hours=(0 < DNI).sum()
    temp=output[:,10]+273 #K
    step_sim=output [:,11]   
    steps_sim=len(output) #Numero de steps en la simulacion
    
    meteoDict={'DNI':DNI.tolist(),'localMeteo':localMeteo}
    
    Demand=DemandData(file_demand,mes_ini_sim,dia_ini_sim,hora_ini_sim,mes_fin_sim,dia_fin_sim,hora_fin_sim) #kWh
    #Preparation of variables depending on the scheme selected
    
    
    #Variable init
    sat_liq=0 #Not used
    sat_vap=0 #Not used
    x_design=0 #Not used
    outProcess_h=0 #Not used
    energStorageMax=0 #kWh
    energyStored=0 #kWh
    porctSensible=0 #Not used
    T_out_HX_C=0 #ot used 
    energStorageMax=0 #kWh  
    T_out_process_C=0 #Not used
    T_in_process_C=0 #Not used
    outProcess_s=0 #Not used
    hProcess_out=0 #Not used
    
    
    if type_integration=="SL_L_RF":    
        
        heatFactor=.5 #Proportion of temperature
        DELTA_T_HX=5 #Degrees for DELTA in the heat Exchanger
        P_op_Mpa=P_op_bar/10
        
    
        
        T_in_K=T_in_C+273
        T_in_process_C=T_in_C
        T_in_process_K=T_in_C+273
        inputProcessState=IAPWS97(P=P_op_Mpa, T=T_in_process_K)
        hProcess_in=inputProcessState.h
    
        #Heat Exchanger design DELTAT    
        T_in_C=T_in_C+DELTA_T_HX
        T_in_K=T_in_C+273
        
        if fluidInput!="oil":
            if T_out_C>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                T_out_C=IAPWS97(P=P_op_Mpa, x=0).T-273
        T_out_K=T_out_C+273
        T_out_process_K=T_out_K
        T_out_process_C=T_out_K-273 #Temp out the process
        outputProcessState=IAPWS97(P=P_op_Mpa, T=T_out_process_K)
        outProcess_s=outputProcessState.s
        hProcess_out=outputProcessState.h
    
        T_out_HX_K=(T_in_process_K+(T_out_K-T_in_process_K)*heatFactor)
        T_out_HX_C=T_out_HX_K-273
        outputHXState=IAPWS97(P=P_op_Mpa, T=T_out_HX_K)
        outHX_s=outputHXState.s #Not used?
        hHX_out=outputHXState.h
        
        #Our design point will be heat the fluid at x%
        T_out_K=(T_in_process_K+(T_out_K-T_in_process_K)*heatFactor)+DELTA_T_HX
        T_out_C=T_out_K-273 
        
        inputState=IAPWS97(P=P_op_Mpa, T=T_in_K) 
        h_in=inputState.h    
        in_s=inputState.s
        in_x=inputState.x
        outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
        out_s=outputState.s
        h_out=outputState.h                                                                                                                                                                                  
        T_av_process_K=(T_in_process_K+T_out_process_K)/2
        
    if type_integration=="SL_L_P" or type_integration=="PL_E_PM":   
        
        P_op_Mpa=P_op_bar/10

        
        T_in_K=T_in_C+273
        T_in_process_C=T_in_C
        T_in_process_K=T_in_K
        
            
        
        inputState=IAPWS97(P=P_op_Mpa, T=T_in_process_K)
        sProcess_in=inputState.s
        hProcess_in=inputState.h  
        
        if fluidInput!="oil":
            if T_out_C>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                T_out_C=IAPWS97(P=P_op_Mpa, x=0).T-273    
    
        T_out_K=T_out_C+273
        T_out_process_K=T_out_K
        T_out_process_C=T_out_C
        outputProcessState=IAPWS97(P=P_op_Mpa, T=T_out_process_K)
        outProcess_s=outputProcessState.s
        hProcess_out=outputProcessState.h    
        
        
        
        inputState=IAPWS97(P=P_op_Mpa, T=T_in_K) 
        h_in=inputState.h    
        in_s=inputState.s
        in_x=inputState.x
        outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
        out_s=outputState.s
        h_out=outputState.h
        
    
    if type_integration=="SL_L_S" or type_integration=="SL_L_S3":

        
        T_max_storage=95+273 #MAx temperature storage
        T_min_storage=80+273 #MIN temperature storage to supply to the process
        flow_rate_design_kgs=3 #Design flow rate
        P_op_Mpa=P_op_bar/10
        
        T_in_K=T_in_C+273
        T_ini_storage=T_in_K #Initial temperature of the storage
        if T_out_C>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
            T_out_C=IAPWS97(P=P_op_Mpa, x=0).T-273-5 
        T_out_K=T_out_C+273
        
        inputState=IAPWS97(P=P_op_Mpa, T=T_in_K) 
        h_in=inputState.h
        in_s=inputState.s
        in_x=inputState.x
        outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
        out_s=outputState.s
        h_out=outputState.h
        
        #Storage calculations for water
        energyStored=0 #Initial storage
        T_avg_K=(T_in_K+T_out_K)/2
        tempAlm=T_out_K-273
        
        almacenamiento=IAPWS97(P=P_op_Mpa, T=T_out_K) #Propiedades en el almacenamiento
        almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
        almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg          
        storage_max_energy=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_out_K))/3600 #Storage capacity in kWh
        
        almacenamiento=IAPWS97(P=P_op_Mpa, T=T_in_K) #Propiedades en el almacenamiento
        almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
        almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg      
        storage_ini_energy=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_in_K))/3600 #Storage capacity in kWh
    
        energStorageMax=storage_max_energy-storage_ini_energy
        
    if type_integration=="SL_L_PS":
        
        P_op_Mpa=P_op_bar/10
        
        T_in_K=T_in_C+273
        
        if fluidInput!="oil":
            if T_out_C>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                T_out_C=IAPWS97(P=P_op_Mpa, x=0).T-273
            T_out_K=T_out_C+273
            tempAlm=T_out_K-273
            inputState=IAPWS97(P=P_op_Mpa, T=T_in_K) 
            h_in=inputState.h
            in_s=inputState.s
            in_x=inputState.x
            outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
            out_s=outputState.s
            h_out=outputState.h
            
            #Storage calculations for water
            energyStored=0 #Initial storage
            T_avg_K=(T_in_K+T_out_K)/2
            almacenamiento=IAPWS97(P=P_op_Mpa, T=T_avg_K) #Propiedades en el almacenamiento
            almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
            almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg
            energStorageMax=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_out_K-T_in_K))/3600 #Storage capacity in kWh
        else:
            T_out_K=T_out_C+273
            tempAlm=T_out_K-273
            energyStored=0 #Initial storage
            T_av_K=(T_in_K+T_out_K)/2
            [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
            energStorageMax=(almVolumen*(1/1000)*(rho_av)*Cp_av*(T_out_K-T_in_K))/3600 #Storage capacity in kWh
            
    
    if type_integration=="SL_S_FW":
 
        
        P_op_Mpa=P_op_bar/10

        energStorageMax=0 #kWh
        energyStored=0 #kWh
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
        
        T_out_K=IAPWS97(P=P_op_Mpa, x=0).T-5 #Heating point
        T_out_C=T_out_K-273 
          
        in_s=initial.s
        outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
        out_s=outputState.s
        h_out=outputState.h
    
    if type_integration=="SL_S_FWS":

        
        P_op_Mpa=P_op_bar/10
        
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
    #    Demand2=Demand*porctSensT_in_Kible
        Demand2=Demand*porctPreHeated
        
    
        
        T_avg_K=(T_in_K+T_out_K)/2
        tempAlm=T_out_K-273
        almacenamiento=IAPWS97(P=P_op_Mpa, T=T_avg_K) #Propiedades en el almacenamiento
        almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
        almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg
        energStorageMax=almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_out_K-T_in_K)/3600 #Storage capacity in kWh
        energyStored=0 #Initial storage
    
    if type_integration=="SL_S_PD":
        
        
        x_design=0.4
        P_op_Mpa=P_op_bar/10
        almVolumen=0 #litros
        energStorageMax=0 #kWh
        energyStored=0 #kWh
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
        
        outputProcessState=IAPWS97(P=P_op_Mpa, x=1)
        outProcess_s=outputProcessState.s
        outProcess_h=outputProcessState.h
        hProcess_out=outProcess_h
        
        #Not used
        porctSensible=0
        sat_vap=0 #Not used
        T_in_process_C=0 #Not used
        T_out_process_C=T_out_C #Not used
        T_out_HX_C=0 #Not used
        
    integrationDesign={'x_design':x_design,'porctSensible':porctSensible,'almVolumen':almVolumen,'energStorageMax':energStorageMax,
                       'T_out_process_C':T_out_process_C,'T_in_process_C':T_in_process_C,'T_out_HX_C':T_out_HX_C}
    

        
    #Declaracion de variables
    theta_transv_rad=np.zeros(steps_sim)
    theta_i_rad=np.zeros(steps_sim)
    theta_i_deg=np.zeros(steps_sim)
    theta_transv_deg=np.zeros(steps_sim)
    IAM_long=np.zeros(steps_sim)
    IAM_t=np.zeros(steps_sim)
    IAM=np.zeros(steps_sim)
    T_in_K=np.zeros(steps_sim)
    T_out_K=np.zeros(steps_sim)
    flow_rate_kgs=np.zeros(steps_sim)
    Perd_termicas=np.zeros(steps_sim)
    flow_rate_rec=np.zeros(steps_sim)
    bypass=list()
    h_in_kJkg=np.zeros(steps_sim)
    Q_prod=np.zeros(steps_sim)
    Q_prod_lim=np.zeros(steps_sim)
    Q_prod_rec=np.zeros(steps_sim)
    Q_defocus=np.zeros(steps_sim)
    SOC=np.zeros(steps_sim)
    Q_charg=np.zeros(steps_sim)
    Q_discharg=np.zeros(steps_sim)
    Q_useful=np.zeros(steps_sim)
    h_out_kJkg=np.zeros(steps_sim)
    flowToHx=np.zeros(steps_sim)
    flowToMix=np.zeros(steps_sim)
    flowDemand=np.zeros(steps_sim)
    T_toProcess_K=np.zeros(steps_sim)
    T_toProcess_C=np.zeros(steps_sim)
    T_alm_K=np.zeros(steps_sim)
    storage_energy=np.zeros(steps_sim)
    
    for i in range(0,steps_sim):
    
        theta_transv_rad[i],theta_i_rad[i]=theta_IAMs(SUN_AZ[i],SUN_ELV[i],beta,orient_az_rad)
    
        #Cálculo del IAM long y transv
        theta_i_deg[i]=theta_i_rad[i]*180/np.pi
        theta_transv_deg[i]=theta_transv_rad[i]*180/np.pi
        
        [IAM_long[i]]=IAM_calc(theta_i_deg[i],0,IAMfile_loc) #Longitudinal
        [IAM_t[i]]=IAM_calc(theta_transv_deg[i],1,IAMfile_loc) #Transversal
        
    #        if IAM_long[i]>1:
    #            IAM_long[i]=1
    #        if IAM_t[i]>1:
    #            IAM_t[i]=1
                
        IAM[i]=IAM_long[i]*IAM_t[i]
        
    
        if i==0:    #Condiciones iniciales
            bypass.append("OFF")
            Q_prod[i]=0
            T_in_K[i]=temp[0] #Ambient temperature 
            T_out_K[i]=0+273
            if type_integration=="SL_L_S" or type_integration=="SL_L_S3":
                T_alm_K[i]=T_ini_storage
                storage_energy[0]=storage_ini_energy
    #            SOC[i]=100*(T_alm_K[i]-273)/(T_max_storage-273)
                SOC[i]=100*energyStored/energStorageMax
            
        else:
    
            if DNI[i]>lim_inf_DNI :#tengo suficiente radiacion o tengo demanda OPERATION
               
                if type_integration=="SL_L_PS":
                    #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 
                    if fluidInput!="oil":                                                                                                            
                        [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationWaterSimple(bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i-1],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                        [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageWaterSimple(Q_prod[i],energyStored,Demand[i],energStorageMax)     
                    else:
                        [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationOilSimple(bypass,T_in_K[i-1],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])                 
                        [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageOilSimple(Q_prod[i],energyStored,Demand[i],energStorageMax)     
     
                if type_integration=="SL_L_S" or type_integration=="SL_L_S3":
                    #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 
                    if fluidInput!="oil":
                         
                        [T_out_K[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_kgs[i]]=operationOnlyStorageWaterSimple(T_max_storage,T_alm_K[i-1],P_op_Mpa,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,flow_rate_design_kgs)
                                                                                                                                           
                        [T_alm_K[i],storage_energy[i],Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputOnlyStorageWaterSimple(P_op_Mpa,T_min_storage,T_max_storage,almVolumen,T_out_K[i],T_alm_K[i-1],Q_prod[i],energyStored,Demand[i],energStorageMax,storage_energy[i-1],storage_ini_energy)      
                    else:
                        pass
    #                    [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i]]=operationOilSimple(bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
    #                    [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageOilSimple(Q_prod[i],energyStored,Demand[i],energStorageMax)     
     
     
                if type_integration=="SL_L_P" or type_integration=="PL_E_PM":
                                    
                    #SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
                    if fluidInput!="oil":
                        flowDemand[i]=Demand[i]/(hProcess_out-hProcess_in)                    
                        [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationWaterSimple(bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                        [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageWaterSimple(Q_prod[i],Demand[i])
                    else: 
                        
                        T_av_process_K=(T_out_process_K+T_in_process_K)/2
                        [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_process_K)    
                        flowDemand[i]=Demand[i]/(Cp_av*(T_out_process_K-T_in_process_K))      
                        [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationOilSimple(bypass,T_in_K[i-1],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])                 
                        [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageOilSimple(Q_prod[i],Demand[i])
    
                if type_integration=="SL_L_RF":
                                    
                    #SL_L_RF Supply level with liquid heat transfer media return boost integration pg52 
                    if fluidInput!="oil":
                        flowDemand[i]=Demand[i]/(hProcess_out-hProcess_in)                    
                        [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationWaterSimple(bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                        if newBypass=="REC":
                            flowToHx[i]=0   #Valve closed no circulation through the HX. The solar field is recirculating                         
    
                        else:
                            #HX simulation
                            Q_prodProcessSide=Q_prod[i]*.9
                            flowToHx[i]=Q_prodProcessSide/(hHX_out-hProcess_in)  
        
                        flowToMix[i]=flowDemand[i]-flowToHx[i]
                        if flowToHx[i]==0:
                            T_toProcess_K[i]=T_in_process_K
                        else:
                            #Brach to mix                        
                            toMixstate=IAPWS97(P=P_op_Mpa, T=T_out_K[i])
                            #Mix
                            T_av_HX_K=(T_in_process_K+T_out_HX_K)/2
                            toProcessstate=IAPWS97(P=P_op_Mpa, T=T_av_HX_K)
                            
                            T_toProcess_C[i]=(flowToMix[i]*hProcess_in+flowToHx[i]*toMixstate.h)/(flowDemand[i]*toProcessstate.cp)
                        T_toProcess_K[i]=T_toProcess_K[i]+273
                        [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageWaterSimple(Q_prod[i],Demand[i])
                    else: 
                        
                        [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_process_K)    
                        flowDemand[i]=Demand[i]/(Cp_av*(T_out_process_K-T_in_process_K))      
                        [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationOilSimple(bypass,T_in_K[i-1],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])                 
                        if newBypass=="REC":
                            flowToHx[i]=0   #Valve closed no circulation through the HX. The solar field is recirculating                         
                        else:
                            #HX simulation
                            Q_prodProcessSide=Q_prod[i]*.9
                            flowToHx[i]=Q_prodProcessSide/(Cp_av*(T_out_HX_K-T_in_process_K))
                            
                        flowToMix[i]=flowDemand[i]-flowToHx[i]
                        #Exit of the heat Echanger
                        [rho_toHX,Cp_toHX,k_toHX,Dv_toHX,Kv_toHX,thermalDiff_toHX,Prant_toHX]=thermalOil(T_out_HX_K)                    
                        #Brach to mix
                        [rho_toMix,Cp_toMix,k_toMix,Dv_toMix,Kv_toMix,thermalDiff_toMix,Prant_toMix]=thermalOil(T_in_process_K)    
                        #Mix
                        #T_av_HX_K=(T_in_process_K+T_out_HX_K)/2 #Ok when are more or less the same flowrate
                        T_av_HX_K=T_in_process_K*(flowToMix[i]/flowDemand[i])+T_out_HX_K*(flowToHx[i]/flowDemand[i]) #When temperatures are very different            
                        [rho_av_HX,Cp_av_HX,k_av_HX,Dv_av_HX,Kv_av_HX,thermalDiff_av_HX,Prant_av_HX]=thermalOil(T_av_HX_K)    
                        if flowToHx[i]==0:
                            T_toProcess_K[i]=T_in_process_K
                        else:
                            T_toProcess_K[i]=(flowToMix[i]*Cp_toMix*T_in_process_K+flowToHx[i]*Cp_toHX*T_out_HX_K)/(flowDemand[i]*Cp_av_HX)
                        T_toProcess_C[i]=T_toProcess_K[i]-273                                      
                        [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageOilSimple(Q_prod[i],Demand[i])
    
                if type_integration=="SL_S_FW":
                     #SL_S_FW Supply level with steam for solar heating of boiler feed water without storage              
                    [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationWaterSimple(bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                    [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageWaterSimple(Q_prod[i],Demand2[i])
                if type_integration=="SL_S_FWS":
                    #SL_S_FW Supply level with steam for solar heating of boiler feed water with storage  
                    [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationWaterSimple(bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                    [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageWaterSimple(Q_prod[i],energyStored,Demand2[i],energStorageMax)     
                if type_integration=="SL_S_PD":
                    #SL_S_PD Supply level with steam for direct steam generation
                    [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationWaterSimple(bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                    [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageWaterSimple(Q_prod[i],Demand[i])
            else: #No hay radiación ni demanda NO OPERATION            
                if type_integration=="SL_L_S" or type_integration=="SL_L_S3":
                    #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 
                    [T_out_K[i],Q_prod[i],T_in_K[i],SOC[i],T_alm_K[i],storage_energy[i]]=offOnlyStorageWaterSimple(T_alm_K[i-1],energStorageMax,energyStored,T_alm_K[i-1],storage_energy[i-1])
    
                    if Demand[i]>0:
                        [T_alm_K[i],storage_energy[i],Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputOnlyStorageWaterSimple(P_op_Mpa,T_min_storage,T_max_storage,almVolumen,T_out_K[i],T_alm_K[i-1],Q_prod[i],energyStored,Demand[i],energStorageMax,storage_energy[i-1],storage_ini_energy)      
                             
                if type_integration=="SL_L_PS":
                    #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 
                    [T_out_K[i],Q_prod[i],T_in_K[i],SOC[i]]=offStorageWaterSimple(bypass,T_in_flag,T_in_C_AR[i],T_in_K[i-1],energStorageMax,energyStored)
                    if Demand[i]>0:
                        [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageWaterSimple(Q_prod[i],energyStored,Demand[i],energStorageMax)                         
                   
                if type_integration=="SL_L_P" or type_integration=="PL_E_PM" or type_integration=="SL_L_RF":
                    #SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
                    [T_out_K[i],Q_prod[i],T_in_K[i]]=offWaterSimple(bypass,T_in_flag,T_in_C_AR[i],T_in_K[i-1])
                if type_integration=="SL_S_FW":
                    #SL_S_FW Supply level with steam for solar heating of boiler feed water without storage 
                    [T_out_K[i],Q_prod[i],T_in_K[i]]=offWaterSimple(bypass,T_in_flag,T_in_C_AR[i],T_in_K[i-1])
                if type_integration=="SL_S_FWS":
                    #SL_S_FWS Supply level with steam for solar heating of boiler feed water with storage 
                    [T_out_K[i],Q_prod[i],T_in_K[i],SOC[i]]=offStorageWaterSimple(bypass,T_in_flag,T_in_C_AR[i],T_in_K[i-1],energStorageMax,energyStored)
                    if Demand2[i]>0:
                        [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageWaterSimple(Q_prod[i],energyStored,Demand2[i],energStorageMax)                         
                if type_integration=="SL_S_PD":
                    #SL_S_PD Supply level with steam for direct steam generation
                    [T_out_K[i],Q_prod[i],T_in_K[i]]=offWaterSimple(bypass,T_in_flag,T_in_C_AR[i],T_in_K[i-1])
    
    processDict={'T_in_flag':T_in_flag,'T_in_C_AR':T_in_C_AR.tolist(),'T_toProcess_C':T_toProcess_C.tolist()}
    
    #---- ANUAL SUMMARY -----------------------------------------------            
    Production_max=sum(Q_prod) #Produccion total en kWh. Asumiendo que se consume todo lo producido
    Production_lim=sum(Q_prod_lim) #Produccion limitada total en kWh
    Demand_anual=sum(Demand) #Demanda energética anual
    solar_fraction_max=100*Production_max/Demand_anual #Fracción solar maxima
    
    tonCo2Saved=Production_lim*co2factor #Tons of Co2 saved
    totalDischarged=(sum(Q_discharg))
    totalCharged=(sum(Q_charg))
    Utilitation_ratio=100*((sum(Q_prod_lim))/(sum(Q_prod)))
    improvStorage=(100*sum(Q_prod_lim)/(sum(Q_prod_lim)-totalDischarged))-100 #Assuming discharged = Charged
    solar_fraction_lim=100*(sum(Q_prod_lim))/Demand_anual 
    Energy_module_max=Production_max/num_modulos_tot
    operation_hours=np.nonzero(Q_prod)
    DNI_anual_irradiation=sum(DNI)/1000 #kWh/year
    Optic_rho_average=(sum(IAM)*rho_optic_0)/steps_sim
    Perd_term_anual=sum(Perd_termicas)/(1000) #kWh/year
    
    annualProdDict={'Q_prod':Q_prod.tolist(),'Q_prod_lim':Q_prod_lim.tolist(),'Demand':Demand.tolist(),'Q_charg':Q_charg.tolist(),
                    'Q_discharg':Q_discharg.tolist(),'Q_defocus':Q_defocus.tolist(),'solar_fraction_max':solar_fraction_max,
                    'solar_fraction_lim':solar_fraction_lim,'improvStorage':improvStorage,'Utilitation_ratio':Utilitation_ratio,
                    'flow_rate_kgs':flow_rate_kgs.tolist()}
    
    
    if finance_study==1 and steps_sim==8759:
        #---- FINANCIAL SIMULATION INPUTS ---------------------------------
    
        #Variable generation para estudio sensibilidad
    #    Tramos=25
    #    IRR=np.zeros(Tramos)
    #    Amort=np.zeros(Tramos)
    #    Fuel_array=np.zeros(Tramos)
    
    

        IPC=2.5 #%
        fuelIncremento=3.5 #% Incremento anual precio fuel
        
        incremento=IPC/100+fuelIncremento/100
    
        Boiler_eff=0.8 #Boiler efficiency to take into account the excess of fuel consumed
        n_years_sim=25 #Number of years for the simulation
        if co2TonPrice>0:
            CO2=1 #Flag to take into account co2 savings in terms of cost per ton emitted
        else:
            CO2=0 #Flag to take into account co2 savings in terms of cost per ton emitted
        
        margin=0.20 #Margen sobre el precio de venta
        distance=400
        [Selling_price,BM_cost,OM_cost_year]=SP_plant_bymargin(num_modulos_tot,num_loops,margin,type_coll)
        [Selling_price2,BM_cost2,OM_cost_year2]=SP_plant_bymargin2(num_modulos_tot,margin,type_coll,distance)
        #Selling_price=370000 #Selling_price of the plant in €. This value overrides the one calculate by the margin function
        #margin=1-(BM_cost/Selling_price) #This value overrides the one calculate by the margin function
        
        #OM_cost_year=4000 #Cost of O&M/year in € #Para fijar un coste de operación
        Selling_price_module=Selling_price/(num_loops*n_coll_loop)
      
        Selling_price=Selling_price*mofINV
        OM_cost_year=OM_cost_year*1
        
        #---- FINANCE ---------------------------------------------------------
        
        if CO2==1:
            co2Savings=tonCo2Saved*co2TonPrice
        else:
            co2Savings=0
        if businessModel=="Llave en mano" or businessModel=="Turnkey project" or businessModel=="turnkey":
            [LCOE,IRR,IRR10,AmortYear,Acum_FCF,FCF,Energy_savings,OM_cost,fuelPrizeArray,Net_anual_savings]=Turn_key(Production_lim,Fuel_price,Boiler_eff,n_years_sim,Selling_price,OM_cost_year,incremento,co2Savings)
            if lang=="spa":        
                TIRscript="TIR para el cliente"
                Amortscript="<b>Amortización: </b> Año "+ str(AmortYear)
                TIRscript10="TIR para el cliente en 10 años"
            if lang=="eng":
                TIRscript="IRR for the client"
                Amortscript="<b>Payback: </b> Year "+ str(AmortYear)
                TIRscript10="IRR for the client 10 years"
    
        
        #Modelo tipo ESE    
        if businessModel=="Compra de energia" or businessModel=="ESCO" or businessModel=="Renting":
            priceReduction=0.8
             #From financing institution poit of view        
            [IRR,IRR10,AmortYear,Acum_FCF,FCF,BenefitESCO,OM_cost,fuelPrizeArray,Energy_savings,Net_anual_savings]=ESCO(priceReduction,Production_lim,Fuel_price,Boiler_eff,n_years_sim,Selling_price,OM_cost_year,incremento,co2Savings)
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
        fuelPrizeArrayList=[]
        Acum_FCFList=[]
        for i in range(0,len(Acum_FCF)):
            if Acum_FCF[i]<0:
                Acum_FCFList.append("("+str(round(abs(Acum_FCF[i])))+")")
            else:
                Acum_FCFList.append(str(round(Acum_FCF[i])))
        
        for i in range(0,len(fuelPrizeArray)):
            Energy_savingsList.append(round(Net_anual_savings[i]))
    
            fuelPrizeArrayList.append(fuelPrizeArray[i])
        
        energy_bill=Demand_anual*Fuel_price
        Solar_savings_lim=Production_lim*Fuel_price
        Solar_savings_max=Production_max*Fuel_price
        
        finance={'AmortYear':AmortYear,'finance_study':finance_study,'CO2':CO2,'co2Savings':co2Savings,
                 'fuelPrizeArrayList':fuelPrizeArrayList,'Acum_FCFList':Acum_FCFList,'Energy_savingsList':Energy_savingsList,
                 'TIRscript':TIRscript,'TIRscript10':TIRscript10,'Amortscript':Amortscript,
                 'co2TonPrice':co2TonPrice,'fuelIncremento':fuelIncremento,'IPC':IPC,'Selling_price':Selling_price,
                 'IRR':IRR,'IRR10':IRR10,'tonCo2Saved':tonCo2Saved,'OM_cost_year':OM_cost_year}
    
    else:
        n_years_sim=0 #No finance simulation
        Acum_FCF=np.array([]) #No finance simulation
        FCF=np.array([]) #No finance simulation
        AmortYear=0 #No finance simulation
        Selling_price=0 #No finance simulation
    #%%
    # ---------------------------------------------------------------------
    # --------------------------- PLOT CONSOLE ----------------------------
    # ---------------------------------------------------------------------
     
    plotVars={'lang':lang,'Production_max':Production_max,'Production_lim':Production_lim,
              'Perd_term_anual':Perd_term_anual,'DNI_anual_irradiation':DNI_anual_irradiation,
              'Area':Area,'num_loops':num_loops,'imageQlty':imageQlty,'plotPath':plotPath,
              'Demand':Demand.tolist(),'Q_prod':Q_prod.tolist(),'Q_prod_lim':Q_prod_lim.tolist(),'type_integration':type_integration,
              'Q_charg':Q_charg.tolist(),'Q_discharg':Q_discharg.tolist(),'DNI':DNI.tolist(),'SOC':SOC.tolist(),
              'Q_useful':Q_useful.tolist(),'Q_defocus':Q_defocus.tolist(),'T_alm_K':T_alm_K.tolist(),
              'n_years_sim':n_years_sim,'Acum_FCF':Acum_FCF.tolist(),'FCF':FCF.tolist(),'m_dot_min_kgs':m_dot_min_kgs,
              'steps_sim':steps_sim,'AmortYear':AmortYear,'Selling_price':Selling_price,
              'in_s':in_s,'out_s':out_s,'T_in_flag':T_in_flag,
              'T_in_C':T_in_C,'T_in_C_AR':T_in_C_AR.tolist(),'T_out_C':T_out_C,
              'outProcess_s':outProcess_s,'T_out_process_C':T_out_process_C,'P_op_bar':P_op_bar,
              'x_design':x_design,'h_in':h_in,'h_out':h_out,'hProcess_out':hProcess_out,'outProcess_h':outProcess_h}
    
    # Annual simulations
    if steps_sim==8759:
        if plots[0]==1: #(0) Sankey plot
            image_base64,sankeyDict=SankeyPlot(sender,ressspiReg,lang,Production_max,Production_lim,Perd_term_anual,DNI_anual_irradiation,Area,num_loops,imageQlty,plotPath)
        if plots[0]==0: #(0) Sankey plot -> no plotting
            sankeyDict={'Production':0,'raw_potential':0,'Thermal_loss':0,'Utilization':0}
        if plots[1]==1: #(1) Production week Winter & Summer
            prodWinterPlot(sender,ressspiReg,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty)   
            prodSummerPlot(sender,ressspiReg,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty)  
        if plots[2]==1 and finance_study==1: #(2) Plot Finance
            financePlot(sender,ressspiReg,lang,n_years_sim,Acum_FCF,FCF,m_dot_min_kgs,steps_sim,AmortYear,Selling_price,plotPath,imageQlty)
        if plots[3]==1: #(3)Plot of Storage first week winter & summer 
            storageWinter(sender,ressspiReg,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty)    
            storageSummer(sender,ressspiReg,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty)    
        if plots[4]==1: #(4) Plot Prod months
            output_excel=prodMonths(sender,ressspiReg,Q_prod,Q_prod_lim,DNI,Demand,lang,plotPath,imageQlty)
    
    # Non-annual simulatios (With annual simuations you cannot see anything)
    if steps_sim!=8759:
        if plots[5]==1: #(5) Theta angle Plot
            thetaAnglesPlot(sender,ressspiReg,step_sim,steps_sim,theta_i_deg,theta_transv_deg,plotPath,imageQlty)
        if plots[6]==1: #(6) IAM angles Plot
            IAMAnglesPlot(sender,ressspiReg,step_sim,IAM_long,IAM_t,IAM,plotPath,imageQlty) 
        if plots[7]==1: #(7) Plot Overview (Demand vs Solar Radiation) 
            demandVsRadiation(sender,ressspiReg,lang,step_sim,Demand,Q_prod,Q_prod_lim,Q_prod_rec,steps_sim,DNI,plotPath,imageQlty)
        if plots[8]==1: #(8) Plot flowrates  & Temp & Prod
            flowRatesPlot(sender,ressspiReg,step_sim,steps_sim,flow_rate_kgs,flow_rate_rec,num_loops,flowDemand,flowToHx,flowToMix,m_dot_min_kgs,T_in_K,T_toProcess_C,T_out_K,T_alm_K,plotPath,imageQlty)
        if plots[9]==1: #(9)Plot Storage non-annual simulation  
            storageAnnual(sender,ressspiReg,SOC,Q_useful,Q_prod,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty)
             
    # Property plots
    if fluidInput!="oil": #WATER
        if plots[10]==1: #(10) Mollier Plot for s-t for Water
            mollierPlotST(sender,ressspiReg,lang,type_integration,in_s,out_s,T_in_flag,T_in_C,T_in_C_AR,T_out_C,outProcess_s,T_out_process_C,P_op_bar,x_design,plotPath,imageQlty)              
        if plots[11]==1: #(11) Mollier Plot for s-h for Water 
            mollierPlotSH(sender,ressspiReg,lang,type_integration,h_in,h_out,hProcess_out,outProcess_h,in_s,out_s,T_in_flag,T_in_C,T_in_C_AR,T_out_C,outProcess_s,T_out_process_C,P_op_bar,x_design,plotPath,imageQlty)  
    if fluidInput=="oil": 
        if plots[12]==1:
            rhoTempPlotOil(sender,ressspiReg,lang,T_out_C,plotPath,imageQlty) #(12) Plot thermal oil properties Rho & Cp vs Temp
        if plots[13]==1:
            viscTempPlotOil(sender,ressspiReg,lang,T_out_C,plotPath,imageQlty) #(13) Plot thermal oil properties Viscosities vs Temp        
    
    # Other plots
    if plots[14]==1: #(14) Plot Production
        productionSolar(sender,ressspiReg,lang,step_sim,DNI,m_dot_min_kgs,steps_sim,Demand,Q_prod,Q_prod_lim,Q_charg,Q_discharg,type_integration,plotPath,imageQlty)
    
    
    #%% 
    
    #Create Report with results (www.ressspi.com uses a customized TEMPLATE called in the function "reportOutput"
    if steps_sim==8759: #The report is only available when annual simulation is performed
        if ressspiReg==-2:
            fileName="results"+str(reg)
            reportsVar={'logo_output':'no_logo','date':inputs['date'],'type_integration':type_integration,
                        'fileName':fileName,'reg':reg,
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
            template_vars=reportOutput(ressspiReg,reportsVar,-1,"",pk,version,os.path.dirname(os.path.dirname(__file__))+'/ressspi',os.path.dirname(os.path.dirname(__file__)))
        
        else:
            template_vars={} 
            reportsVar={'logo_output':'no_logo','version':version,'type_integration':type_integration,
                        'energyStored':energyStored,"location":localMeteo,
                        'Area_total':Area_total,'n_coll_loop':n_coll_loop,
                        'num_loops':num_loops,'m_dot_min_kgs':m_dot_min_kgs,
                        'Production_max':Production_max,'Production_lim':Production_lim,
                        'Demand_anual':Demand_anual,'solar_fraction_max':solar_fraction_max,
                        'solar_fraction_lim':solar_fraction_lim,'DNI_anual_irradiation':DNI_anual_irradiation}
            reportsVar.update(finance)
            reportsVar.update(confReport)
            reportsVar.update(annualProdDict)
            reportsVar.update(modificators)
            reportOutputOffline(reportsVar)
    else:
        template_vars={}
        reportsVar={}
        
    return(template_vars,plotVars,reportsVar,version)

# ----------------------------------- END RESSSPI -------------------------
# -------------------------------------------------------------------------
    #%% 
       

    
    
#Plot Control ---------------------------------------
imageQlty=200

plots=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,0]
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
#(12) P- Plot thermal oil properties Rho & Cp vs Temp
#(13) P- Plot thermal oil properties Viscosities vs Temp 
#(14) Plot Production 

finance_study=1

mes_ini_sim=1
dia_ini_sim=1
hora_ini_sim=1

mes_fin_sim=12 
dia_fin_sim=31
hora_fin_sim=24



# -------------------- FINE TUNNING CONTROL ---------
mofINV=1.6 #Sobre el coste de inversion
mofDNI=1.1  #Corrección a fichero Meteonorm
mofProd=.9 #Factor de seguridad a la producción de los módulos

# -------------------- SIZE OF THE PLANT ---------
num_loops=4  
n_coll_loop=4

#SL_L_P -> Supply level liquid parallel integration without storage
#SL_L_PS -> Supply level liquid parallel integration with storage
#SL_L_RF -> Supply level liquid return flow boost
#SL_S_FW -> Supply level solar steam for heating of boiler feed water without storage
#SL_S_FWS -> Supply level solar steam for heating of boiler feed water with storage
#SL_S_PD -> Supply level solar steam for direct solar steam generation 
#SL_L_S -> Storage
#SL_L_S3 -> Storage plus pasteurizator plus washing
type_integration="SL_L_PS"
almVolumen=5000 #litros

# --------------------------------------------------
confReport={'lang':'spa','sender':'solatom','cabecera':'Resultados de la <br> simulación','mapama':0}
modificators={'mofINV':mofINV,'mofDNI':mofDNI,'mofProd':mofProd}
desginDict={'num_loops':num_loops,'n_coll_loop':n_coll_loop,'type_integration':type_integration,'almVolumen':almVolumen}
simControl={'finance_study':finance_study,'mes_ini_sim':mes_ini_sim,'dia_ini_sim':dia_ini_sim,'hora_ini_sim':hora_ini_sim,'mes_fin_sim':mes_fin_sim,'dia_fin_sim':dia_fin_sim,'hora_fin_sim':hora_fin_sim}    
# ---------------------------------------------------

ressspiReg=-2 #0 if new record; -2 if it comes from www.ressspi.com

if ressspiReg==0:
    #To perform simulations from command line using hardcoded inputs
    inputsDjango={}
    last_reg=666
else:
    #To perform simulations from command line using inputs from django
    inputsDjango= {'date': '2018-10-14', 'name': 'miguel', 'email': 'mfrasquetherraiz@gmail.com', 'industry': 'replica_indio', 'sectorIndustry': 'Laundries', 'fuel': 'Gasoil-B', 'fuelPrice': 9.823182711198428e-05, 'co2TonPrice': 0.0, 'co2factor': 0.00027, 'fuelUnit': 'eur_kWh', 'businessModel': 'turnkey', 'location': 'Ahmednagar', 'location_aux': '', 'surface': 50000, 'terrain': '', 'distance': 50000, 'orientation': 'NS', 'inclination': 'flat', 'shadows': 'free', 'fluid': 'water', 'pressure': 3.0, 'pressureUnit': 'bar', 'tempIN': 30.0, 'tempOUT': 130.0, 'connection': 'storage', 'process': '', 'demand': 5000.0, 'demandUnit': 'MWh', 'hourINI': 8, 'hourEND': 24, 'Mond': 0.167, 'Tues': 0.167, 'Wend': 0.167, 'Thur': 0.167, 'Fri': 0.167, 'Sat': 0.167, 'Sun': 0.0, 'Jan': 0.083, 'Feb': 0.083, 'Mar': 0.083, 'Apr': 0.083, 'May': 0.083, 'Jun': 0.083, 'Jul': 0.083, 'Aug': 0.083, 'Sep': 0.083, 'Oct': 0.083, 'Nov': 0.083, 'Dec': 0.083, 'last_reg': 269}   
    last_reg=inputsDjango['last_reg']
   
#[jSonResults,plotVars,reportsVar,version]=ressspiSIM(ressspiReg,inputsDjango,plots,imageQlty,confReport,modificators,desginDict,simControl,last_reg)

