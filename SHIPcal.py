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

from General_modules.func_General import DemandData,waterFromGrid,waterFromGrid_trim,thermalOil,reportOutputOffline, moltenSalt,waterFromGrid_v3 
from General_modules.demandCreator_v1 import demandCreator
from General_modules.fromDjangotoSHIPcal import djangoReport
from Solar_modules.EQSolares import SolarData
from Solar_modules.EQSolares import theta_IAMs_v2
from Solar_modules.EQSolares import IAM_calc
from Finance_modules.FinanceModels import SP_plant_costFunctions
from Integration_modules.integrations import *
from Plot_modules.plottingSHIPcal import *


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
        plotPath=os.path.dirname(os.path.realpath(__file__))+'/CIMAV/results' #FilePath for images when called cimav
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
    elif sender=='CIMAV': #The request comes from CIMAV front-end
        from CIMAV.CIMAV_modules.fromDjangotoRessspivCIMAV import djangoReport as djangoReportCIMAV
        from CIMAV.meteorologic_database.meteoDBmanager import Lat_Huso
        from CIMAV.CIMAV_modules.CIMAV_collectors import CIMAV_collectors,IAM_fiteq,IAM_calculator #Imports a CIMAV's module to return the parameters of collectors supported by CIMAV
        from CIMAV.CIMAV_modules.incidence_angle import theta_IAMs_v2 as theta_IAMs_CIMAV
        from CIMAV.CIMAV_modules.CIMAV_financeModels import Turn_key,ESCO,CIMAV_plant_costFunctions
    
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
    
    #%%
    # BLOCK 1.2 - PARAMETERS <><><><><><><><><><><><><><><><><><><><><><><><><><><>
    
    #--> Finance parameters
    fuelCostRaise=3.5 # Annual increase of fuel price [%]
    
    # Annual increase of the price of money through Consumer Price Index [%]
    if sender == 'CIMAV':
        CPI=5 # 5 for México
    else:
        CPI=2.5 # 2.5 for Spain 
        
    costRaise=CPI/100+fuelCostRaise/100
    
    n_years_sim=25 # Collector life in years & number of years for the simulation [years]
    
    
    #--> Process parameters
    
    lim_inf_DNI=200 # Minimum temperature to start production [W/m²]
    m_dot_min_kgs=0.08 # Minimum flowrate before re-circulation [kg/s]
    coef_flow_rec=2 # Multiplier for flowrate when recirculating [-]
    Boiler_eff=0.8 # Boiler efficiency to take into account the excess of fuel consumed [-]
    
        ## SL_L_RF
    heatFactor=.5 # Percentage of temperature variation (T_out - T_in) provided by the heat exchanger (for design) 
    DELTA_T_HX=5 # Degrees for temperature delta experienced in the heat exchanger (for design) 
    HX_eff=0.9 # Simplification for HX efficiency
        ## SL_L_S
    DELTA_ST=30 # Temperature delta over the design process temp for the storage
    flow_rate_design_kgs=2 # Design flow rate (fix value for SL_L_S)
    
    
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
    
    elif sender=='CIMAV': #Use one of the collectors supported by CIMAV
        type_coll=inputsDjango['collector_type']#The collector datasheet will have this name
        Area_coll,rho_optic_0,eta1,eta2,mdot_test,Long,weight=CIMAV_collectors(type_coll) 
        IAM_file='defaultCollector.csv' #Se puede borrar despues 
        REC_type=1#Se puede borrar despues 
        IAM_folder=os.path.dirname(os.path.realpath(__file__))+"/Collector_modules/"
    
    else: #Using other collectors (to be filled with customized data)
        
        ## IAM 
        IAM_file='defaultCollector.csv'
        IAM_folder=os.path.dirname(__file__)+"/Collector_modules/"
        IAMfile_loc=IAM_folder+IAM_file
        
        ## Solar collector characteristics
        REC_type=1 #Type of receiver used (1 -> Schott receiver tube)
        Area_coll=26.4 #Aperture area of collector per module [m²]
        rho_optic_0=0.75583 #Optical eff. at incidence angle=0 [º]
        Long=5.28 #Longitude of each module [m]
        
    Area=Area_coll*n_coll_loop #Area of aperture per loop [m²] Used later
    Area_total=Area*num_loops #Total area of aperture [m²] Used later
    num_modulos_tot=n_coll_loop*num_loops
    
        ## --> TO BE IMPLEMENTED Not used for the moment, it will change in future versions
        
    orientation="NS"
    inclination="flat" 
    shadowInput="free"
    terreno="clean_ground"

    beta=0 #Pitch not implemented [rad]
    orient_az_rad=0 #Orientation not implemented [rad]
    roll=0 #Roll not implemented [rad]

    
    # --> Front-end inputs
    
    if origin==-2: #Simulation called from front-end -> www.ressspi.com
        
        #Retrieve front-end inputs
        [inputs,annualConsumptionkWh,reg,P_op_bar,monthArray,weekArray,dayArray]=djangoReport(inputsDjango)
         
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
       
#        file_demand=demandCreator(annualConsumptionkWh,dayArray,weekArray,monthArray)
        file_demand = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi_offline/demand_files/demand_con.csv", sep=',')   

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
        [inputs,annualConsumptionkWh,reg,P_op_bar,monthArray,weekArray,dayArray]=djangoReportCIMAV(inputsDjango)
        
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
        [inputs,annualConsumptionkWh,reg,P_op_bar,monthArray,weekArray,dayArray]=djangoReport(inputsDjango)
        
        ## METEO (free available meteo sets)
        locationFromFrontEnd=inputs['location']
        
        meteoDB = pd.read_csv(os.path.dirname(__file__)+"/Meteo_modules/meteoDB.csv", sep=',')  
        localMeteo=meteoDB.loc[meteoDB['Provincia'] == locationFromFrontEnd, 'meteoFile'].iloc[0]
        file_loc=os.path.dirname(__file__)+"/Meteo_modules/"+localMeteo
        Lat=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Latitud'].iloc[0]
        Huso=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Huso'].iloc[0]
        
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
        localMeteo="Fargo_SAM.dat" #Be sure this location is included in SHIPcal DB
        if sender=='solatom': #Use Solatom propietary meteo DB. This is only necessary to be able to use solatom data from terminal
            meteoDB = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/meteoDB.csv", sep=',') 
            file_loc=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/"+localMeteo       
            Lat=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Latitud'].iloc[0]
            Huso=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Huso'].iloc[0]
        else:
            meteoDB = pd.read_csv(os.path.dirname(__file__)+"/Meteo_modules/meteoDB.csv", sep=',')  
            file_loc=os.path.dirname(__file__)+"/Meteo_modules/"+localMeteo
            Lat=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Latitud'].iloc[0]
            Huso=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Huso'].iloc[0]
        
        ## INTEGRATION
        type_integration=desginDict['type_integration'] # Type of integration scheme from IEA SHC Task 49 "Integration guidelines" http://task49.iea-shc.org/Data/Sites/7/150218_iea-task-49_d_b2_integration_guideline-final.pdf
        almVolumen=desginDict['almVolumen'] # Storage capacity [litres]    
        
        ## INDUSTRIAL APPLICATION
            #>> PROCESS
        fluidInput="steam" #"water" "steam" "oil" "moltenSalt"
        T_process_in=120 #HIGH - Process temperature [ºC]
        T_process_out=60 #LOW - Temperature at the return of the process [ºC]
        P_op_bar=6 #[bar] 
        
        # Not implemented yet
        distanceInput=15 #From the solar plant to the network integration point [m]
        surfaceAvailable=500 #Surface available for the solar plant [m2]
            
        ## ENERGY DEMAND
#        dayArray=[0,0,0,0,0,0,0,1/10,1/10,1/10,1/10,1/10,1/10,1/10,1/10,1/10,1/10,1/10,0,0,0,0,0,0] #12 hours day profile
        dayArray=[1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24] #24 hours day profile
       
        weekArray=[0.143,0.143,0.143,0.143,0.143,0.143,0.143] #No weekends
        monthArray=[1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12] #Whole year     
        totalConsumption=1200*8760 #[kWh]
        file_demand=demandCreator(totalConsumption,dayArray,weekArray,monthArray)
        
        ## FINANCE
        businessModel="turnkey"
        fuel="Gasoil-B" #Type of fuel
        Fuel_price=0.05 #Price of fossil fuel [€/kWh]
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
    Energy_Before=DemandData(file_demand,month_ini_sim,day_ini_sim,hour_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim) # [kWh]
    Energy_Before_annual=sum(Energy_Before) #This should be exactly the same as annualConsumptionkWh for annual simulations
    Demand=Boiler_eff*Energy_Before #Demand of energy after the boiler [kWh]
    
    
    if co2TonPrice>0:
        CO2=1 #Flag to take into account co2 savings in terms of cost per ton emitted
    else:
        CO2=0 #Flag to take into account co2 savings in terms of cost per ton emitted
    
    
    
    # --> Meteo variables
   
    output,hour_year_ini,hour_year_fin=SolarData(file_loc,Lat,Huso,month_ini_sim,day_ini_sim,hour_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim,sender)

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

    SUN_ELV=output[:,5] # Sun elevation [rad]
    SUN_AZ=output[:,6] # Sun azimuth [rad]
    DNI=output[:,9] # Direct Normal Irradiation [W/m²]
    temp=output[:,10]+273 # Ambient temperature [K] 
    step_sim=output [:,11] #Array containing the simulation steps 
    steps_sim=len(output) # Number of steps in the simulation

    
    DNI=DNI*mofDNI # DNI modified if needed. This is necessary to take into account 
    meteoDict={'DNI':DNI.tolist(),'localMeteo':localMeteo}

#%%
# ------------------------------------------------------------------------------------
# BLOCK 2 - SOLAR SIMULATION --------------------------------------------------
# ------------------------------------------------------------------------------------
    # BLOCK 2.1 - PROCESS VARIABLES <><><><><><><><><><><><><><><><><><><><><><><><><><><>      
    # IEA SHC Task 49 "Integration guidelines" http://task49.iea-shc.org/Data/Sites/7/150218_iea-task-49_d_b2_integration_guideline-final.pdf

    # --> Process variable init
    
    sat_liq=0 #Not used
    sat_vap=0 #Not used
    x_design=0 #Not used
    outProcess_h=0 #Not used
    energStorageMax=0 #kWh
    energyStored=0 #kWh
    porctSensible=0 #Not used
    T_out_HX_C=0 #Not used 
    T_out_process_C=0 #Not used
    T_in_process_C=0 #Not used
    outProcess_s=0 #Not used
    hProcess_out=0 #Not used
    in_s=0
    out_s=0
    h_in=0
    h_out=0
    
    
    #Temperature of the make-up water
    T_in_C_AR=waterFromGrid_v3(file_loc,sender)
    #Trim the T_in_C_AR [8760] to the simulation frame 
    T_in_C_AR=waterFromGrid_trim(T_in_C_AR,month_ini_sim,day_ini_sim,hour_ini_sim,month_fin_sim,day_fin_sim,hour_fin_sim)

    #By default water flows in closed loop
    T_in_flag=1 #Flag 1 means closed loop (water flowing from a piping closed loop); Flag 0 means open loop (water flowing from the grid)
        
    # --> Integrations: 
        # SL_L_RF Supply level with liquid heat transfer media solar return flow boost
        
    if type_integration=="SL_L_RF": 

        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
        T_out_C=T_process_in #The outlet temperature at the solar field is the same than the process temperature

        
        T_in_K=T_in_C+273
        T_in_process_C=T_in_C
        T_in_process_K=T_in_C+273
        inputProcessState=IAPWS97(P=P_op_Mpa, T=T_in_process_K)
        hProcess_in=inputProcessState.h
    
        #Heat Exchanger design DELTAT    
        T_in_C=T_in_C+DELTA_T_HX
        T_in_K=T_in_C+273
        
        if fluidInput=="water":
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
    
    # ----------------------------------------
        # SL_L_P => Supply level with liquid heat transfer media parallel integration
        # PL_E_PM => Process level external HEX for heating of product or process medium
        
    if type_integration=="SL_L_P" or type_integration=="PL_E_PM":   
           
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
        T_out_C=T_process_in #The outlet temperature at the solar field is the same than the process temperature
        
        T_in_K=T_in_C+273
        T_in_process_C=T_in_C
        T_in_process_K=T_in_K
        
        if fluidInput=="water":
            inputState=IAPWS97(P=P_op_Mpa, T=T_in_process_K)
            hProcess_in=inputState.h  
            if T_out_C>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                T_out_C=IAPWS97(P=P_op_Mpa, x=0).T-273    
    
        T_out_K=T_out_C+273
        T_out_process_K=T_out_K
        T_out_process_C=T_out_C
        if fluidInput=="water":
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
        
    # ----------------------------------------
        # SL_L_S => Supply level with liquid heat transfer media solar heating of storages
        # SL_L_S3 => Supply level with liquid heat transfer media solar heating of storages (Pasteurization case)
        
    if type_integration=="SL_L_S" or type_integration=="SL_L_S3":
        
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
        T_out_C=T_process_in #The outlet temperature at the solar field is the same than the process temperature
        
        
        T_in_K=T_in_C+273
        T_ini_storage=T_in_K #Initial temperature of the storage
        
        if fluidInput=="water": # Only applies to water
            if T_out_C>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                T_out_C=IAPWS97(P=P_op_Mpa, x=0).T-273-5 
        
        T_out_K=T_out_C+273
       
        T_min_storage=T_out_C+273 #MIN temperature storage to supply to the process # Process temp [K]  
        
        if fluidInput=="water": # Only applies to water
            if T_out_C+DELTA_ST>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                T_max_storage=IAPWS97(P=P_op_Mpa, x=0).T #Max temperature storage [K]
            else:
                T_max_storage=T_out_C+DELTA_ST+273 #Max temperature storage [K]
        else:
            T_max_storage=T_out_C+DELTA_ST+273 #Max temperature storage [K] 
        
        if fluidInput=="water": # WATER STORAGE
            inputState=IAPWS97(P=P_op_Mpa, T=T_in_K) 
            h_in=inputState.h
            in_s=inputState.s
            in_x=inputState.x
            outputState=IAPWS97(P=P_op_Mpa, T=T_out_K)
            out_s=outputState.s
            h_out=outputState.h
            
            #Storage calculations for water
            energyStored=0 # Initially the storage is empty
            T_avg_K=(T_in_K+T_out_K)/2
            
            almacenamiento=IAPWS97(P=P_op_Mpa, T=T_out_K) #Propiedades en el almacenamiento
            almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
            almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg          
            storage_max_energy=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_max_storage))/3600 #Storage capacity in kWh
            
            almacenamiento=IAPWS97(P=P_op_Mpa, T=T_in_K) #Propiedades en el almacenamiento
            almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
            almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg      
            storage_ini_energy=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_in_K))/3600 #Storage capacity in kWh
        
            storage_min_energy=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_out_K))/3600 #Storage capacity in kWh
            energStorageUseful=storage_max_energy-storage_min_energy # Maximum storage capacity in kWh
        
            energStorageMax=storage_max_energy-storage_ini_energy # Maximum storage capacity in kWh
        
        if fluidInput=="oil": # THERMAL OIL STORAGE
                       
            #Storage calculations for water
            energyStored=0 # Initially the storage is empty
            T_avg_K=(T_in_K+T_out_K)/2
            
            # Properties for MAX point
                 
            [storage_max_rho,storage_max_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_max_storage)
            storage_max_energy=(almVolumen*(1/1000)*(storage_max_rho)*storage_max_Cp*(T_max_storage))/3600 #Storage capacity in kWh
            
            [storage_ini_rho,storage_ini_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_in_K)
            storage_ini_energy=(almVolumen*(1/1000)*(storage_ini_rho)*storage_ini_Cp*(T_in_K))/3600 #Storage capacity in kWh
        
            [storage_min_rho,storage_min_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_out_K)
            storage_min_energy=(almVolumen*(1/1000)*(storage_min_rho)*storage_min_Cp*(T_out_K))/3600 #Storage capacity in kWh
            
            energStorageUseful=storage_max_energy-storage_min_energy # Maximum storage capacity in kWh
        
            energStorageMax=storage_max_energy-storage_ini_energy # Maximum storage capacity in kWh
    
        if fluidInput=="moltenSalt": # MOLTEN SALTS STORAGE
                       
            #Storage calculations for water
            energyStored=0 # Initially the storage is empty
            T_avg_K=(T_in_K+T_out_K)/2
            
            # Properties for MAX point
            [storage_max_rho,storage_max_Cp,k,Dv]=moltenSalt(T_max_storage)
            storage_max_energy=(almVolumen*(1/1000)*(storage_max_rho)*storage_max_Cp*(T_max_storage))/3600 #Storage capacity in kWh
            
            [storage_ini_rho,storage_ini_Cp,k,Dv]=moltenSalt(T_in_K)
            storage_ini_energy=(almVolumen*(1/1000)*(storage_ini_rho)*storage_ini_Cp*(T_in_K))/3600 #Storage capacity in kWh
        
            [storage_min_rho,storage_min_Cp,k,Dv]=moltenSalt(T_out_K)
            storage_min_energy=(almVolumen*(1/1000)*(storage_min_rho)*storage_min_Cp*(T_out_K))/3600 #Storage capacity in kWh
            
            energStorageUseful=storage_max_energy-storage_min_energy # Maximum storage capacity in kWh
        
            energStorageMax=storage_max_energy-storage_ini_energy # Maximum storage capacity in kWh
    
    
    # ----------------------------------------
        # SL_L_PS => Supply level with liquid heat transfer media parallel integration with storage
        
    if type_integration=="SL_L_PS":
              
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
        T_out_C=T_process_in #The outlet temperature at the solar field is the same than the process temperature

        
        T_in_K=T_in_C+273
        
        if fluidInput=="water":
            if T_out_C>IAPWS97(P=P_op_Mpa, x=0).T-273: #Make sure you are in liquid phase
                T_out_C=IAPWS97(P=P_op_Mpa, x=0).T-273
            T_out_K=T_out_C+273
#            tempAlm=T_out_K-273
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
        
        if fluidInput=="oil":
            T_out_K=T_out_C+273
            energyStored=0 #Initial storage
            T_av_K=(T_in_K+T_out_K)/2
            [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
            energStorageMax=(almVolumen*(1/1000)*(rho_av)*Cp_av*(T_out_K-T_in_K))/3600 #Storage capacity in kWh
        
        if fluidInput=="moltenSalt":
            T_out_K=T_out_C+273
            energyStored=0 #Initial storage
            T_av_K=(T_in_K+T_out_K)/2
            [rho_av,Cp_av,k,Dv]=moltenSalt(T_av_K)
            energStorageMax=(almVolumen*(1/1000)*(rho_av)*Cp_av*(T_out_K-T_in_K))/3600 #Storage capacity in kWh
                
    # ---------------------------------------- 
        # SL_S_FW => Supply level with steam solar heating of boiler feed water
        
    if type_integration=="SL_S_FW":
        
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
        T_out_C=T_process_in #The outlet temperature at the solar field is the same than the process temperature
        
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
    
    # ----------------------------------------
    # SL_S_FWS => Supply level with steam solar heating of boiler feed water including storage
    
    if type_integration=="SL_S_FWS":
            
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
        energyStored=0 #Initial storage
        
    # ---------------------------------------- 
        # SL_S_MW => Supply level with steam solar heating of boiler make-up water
        
    if type_integration=="SL_S_MW":
 
        T_in_flag=0 #Flag 1 means closed loop (water flowing from a piping closed loop); Flag 0 means open loop (water flowing from the grid)
        
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
        T_out_C=T_process_in #The outlet temperature at the solar field is the same than the process temperature
        
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
    
    # ----------------------------------------
    #SL_S_MWS => Supply level with steam solar heating of boiler make-up water including storage
    
    if type_integration=="SL_S_MWS":
        
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
        energyStored=0 #Initial storage
    
    # ----------------------------------------
        # SL_S_PD => Supply level with steam direct solar steam generation
        
    if type_integration=="SL_S_PD":
        
        
        P_op_Mpa=P_op_bar/10 #The solar field will use the same pressure than the process 
        T_in_C=T_process_out #The inlet temperature at the solar field is the same than the return of the process
       
        x_design=0.4

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
    
    
    # --> Simulation Loop variable init
    
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
    
    if sender=='CIMAV':
        blong,nlong = IAM_fiteq(type_coll,1)
        btrans,ntrans = IAM_fiteq(type_coll,2)
    
    # BLOCK 2.2 - SIMULATION ANNUAL LOOP <><><><><><><><><><><><><><><><><><><><><><><><><><><>        
    
    # --> Instant = 0 (Initial conditions)
    bypass.append("OFF")
    Q_prod[0]=0
    T_in_K[0]=temp[0] #Ambient temperature 
    T_out_K[0]=temp[0] #Ambient temperature 
    if type_integration=="SL_L_S" or type_integration=="SL_L_S3":
        T_alm_K[0]=T_ini_storage
        storage_energy[0]=storage_ini_energy
    #            SOC[i]=100*(T_alm_K[i]-273)/(T_max_storage-273)
        SOC[0]=100*energyStored/energStorageMax

        
    for i in range(1,steps_sim): #--> <><><><>< ANNUAL SIMULATION LOOP <><><><><><><><><><><><>
        
    # --> IAM calculation           

        if sender=='solatom': #Using Solatom's IAMs
            if SUN_ELV[i]>0:
                theta_transv_deg[i],theta_i_deg[i]=theta_IAMs_v2(SUN_AZ[i],SUN_ELV[i],beta,orient_az_rad,roll)
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
            lim_inf_DNI=-(eta1*Tm_Ta + eta2*Tm_Ta**2)/rho_optic_0 
            
        else:               # Using default's IAMs 
            if SUN_ELV[i]>0:
                theta_transv_deg[i],theta_i_deg[i]=theta_IAMs_v2(SUN_AZ[i],SUN_ELV[i],beta,orient_az_rad,roll)
                theta_i_deg[i]=abs(theta_i_deg[i])
                [IAM_long[i]]=IAM_calc(theta_i_deg[i],0,IAMfile_loc) #Longitudinal
                [IAM_t[i]]=IAM_calc(theta_transv_deg[i],1,IAMfile_loc) #Transversal
                IAM[i]=IAM_long[i]*IAM_t[i]
            else:
                IAM_long[i]=0
                IAM_t[i]=0
                IAM[i]=IAM_long[i]*IAM_t[i]

            
        if DNI[i]>lim_inf_DNI :# Status: ON -> There's enough DNI to start the system
           
            if type_integration=="SL_L_PS":
                #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 
                
                [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i-1],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageSimple(Q_prod[i],energyStored,Demand[i],energStorageMax)     
           
            elif type_integration=="SL_L_S" or type_integration=="SL_L_S3":
                #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 
                
                [T_out_K[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_kgs[i]]=operationOnlyStorageSimple(fluidInput,T_max_storage,T_alm_K[i-1],P_op_Mpa,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,flow_rate_design_kgs)

                #Storage control
                [T_alm_K[i],storage_energy[i],Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputOnlyStorageSimple(fluidInput,P_op_Mpa,T_min_storage,T_max_storage,almVolumen,T_out_K[i],T_alm_K[i-1],Q_prod[i],energyStored,Demand[i],energStorageMax,storage_energy[i-1],storage_ini_energy,storage_min_energy,energStorageUseful,storage_max_energy)      
                
 
            elif type_integration=="SL_L_P" or type_integration=="PL_E_PM":     
                #SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
                
                if fluidInput=="water":
                    flowDemand[i]=Demand[i]/(hProcess_out-hProcess_in)#Not used, only for S_L_RF                  
                     
                if fluidInput=="oil": 
                    T_av_process_K=(T_out_process_K+T_in_process_K)/2
                    [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_process_K)    
                    flowDemand[i]=Demand[i]/(Cp_av*(T_out_process_K-T_in_process_K)) #Not used, only for S_L_RF         
                
                if fluidInput=="moltenSalt": 
                    T_av_process_K=(T_out_process_K+T_in_process_K)/2
                    [rho_av,Cp_av,k,Dv]=moltenSalt(T_av_process_K)    
                    flowDemand[i]=Demand[i]/(Cp_av*(T_out_process_K-T_in_process_K)) #Not used, only for S_L_RF         
            
                [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageSimple(Q_prod[i],Demand[i])
                                    
            elif type_integration=="SL_L_RF":            
                #SL_L_RF Supply level with liquid heat transfer media return boost integration pg52 
                
                if fluidInput=="water":
                    flowDemand[i]=Demand[i]/(hProcess_out-hProcess_in)                    
                    [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                    if newBypass=="REC":
                        flowToHx[i]=0   #Valve closed no circulation through the HX. The solar field is recirculating                         

                    else:
                        #HX simulation
                        Q_prodProcessSide=Q_prod[i]*HX_eff #Evaluation of the Energy production after the HX
                        flowToHx[i]=Q_prodProcessSide/(hHX_out-hProcess_in)  
                        Q_prod[i]=Q_prodProcessSide #I rename the Qprod to QprodProcessSide since this is the energy the system is transfering the process side
                    
                    flowToMix[i]=flowDemand[i]-flowToHx[i]
                    if flowToHx[i]==0:
                        T_toProcess_K[i]=T_in_process_K
                    else:
                        #Branch from HX to mix                        
                        toMixstate=IAPWS97(P=P_op_Mpa, T=T_out_K[i]-DELTA_T_HX)
                        #Mix
                        T_av_HX_K=(T_in_process_K+T_out_HX_K)/2
                        toProcessstate=IAPWS97(P=P_op_Mpa, T=T_av_HX_K)
                        
                        if flowDemand[i]==0: #If there's no demand then T_toProcss_C[i]=0
                            T_toProcess_C[i]=0
                        else:
                            T_toProcess_C[i]=(flowToMix[i]*hProcess_in+flowToHx[i]*toMixstate.h)/(flowDemand[i]*toProcessstate.cp)
                    T_toProcess_K[i]=T_toProcess_K[i]+273
                    [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageSimple(Q_prod[i],Demand[i])
                
                else: 
                    
                    [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_process_K)    
                    flowDemand[i]=Demand[i]/(Cp_av*(T_out_process_K-T_in_process_K)) 
                                                                                                                                
                    [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                    
                    if newBypass=="REC":
                        flowToHx[i]=0   #Valve closed no circulation through the HX. The solar field is recirculating                         
                    else:
                        #HX simulation
                        Q_prodProcessSide=Q_prod[i]*HX_eff
                        Q_prod[i]=Q_prodProcessSide #I rename the Qprod to QprodProcessSide since this is the energy the system is transfering the process side
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
                    [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageSimple(Q_prod[i],Demand[i])

            elif type_integration=="SL_S_FW" or type_integration=="SL_S_MW":
                #SL_S_FW Supply level with steam for solar heating of boiler feed water without storage              
                
                [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageSimple(Q_prod[i],Demand2[i])
            
            elif type_integration=="SL_S_FWS" or type_integration=="SL_S_MWS":
                #SL_S_FW Supply level with steam for solar heating of boiler feed water with storage  
                
                [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageSimple(Q_prod[i],energyStored,Demand2[i],energStorageMax)     
            
            elif type_integration=="SL_S_PD":
                #SL_S_PD Supply level with steam for direct steam generation
                
                [T_out_K[i],flow_rate_kgs[i],Perd_termicas[i],Q_prod[i],T_in_K[i],flow_rate_rec[i],Q_prod_rec[i],newBypass]=operationSimple(fluidInput,bypass,T_in_flag,T_in_K[i-1],T_in_C_AR[i],T_out_K[i-1],T_in_C,P_op_Mpa,bypass[i-1],T_out_C,temp[i],REC_type,theta_i_rad[i],DNI[i],Long,IAM[i],Area,n_coll_loop,rho_optic_0,num_loops,mofProd,coef_flow_rec,m_dot_min_kgs,Q_prod_rec[i-1])
                [Q_prod_lim[i],Q_defocus[i],Q_useful[i]]=outputWithoutStorageSimple(Q_prod[i],Demand[i])
        
        else: # Status: OFF -> There's not enough DNI to put the solar plant in production     
            
            if type_integration=="SL_L_S" or type_integration=="SL_L_S3":
                #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 

                [T_out_K[i],Q_prod[i],T_in_K[i],SOC[i],T_alm_K[i],storage_energy[i]]=offOnlyStorageSimple(T_alm_K[i-1],energStorageMax,energyStored,T_alm_K[i-1],storage_energy[i-1],SOC[i-1]) 
                if Demand[i]>0:
                    [T_alm_K[i],storage_energy[i],Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputOnlyStorageSimple(fluidInput,P_op_Mpa,T_min_storage,T_max_storage,almVolumen,T_out_K[i],T_alm_K[i-1],Q_prod[i],energyStored,Demand[i],energStorageMax,storage_energy[i-1],storage_ini_energy,storage_min_energy,energStorageUseful,storage_max_energy)           
                
                        
            elif type_integration=="SL_L_PS":
                #SL_L_PS Supply level with liquid heat transfer media Parallel integration with storeage pg52 
                
                [T_out_K[i],Q_prod[i],T_in_K[i],SOC[i]]=offStorageSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i],energStorageMax,energyStored)
                if Demand[i]>0:
                    [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageSimple(Q_prod[i],energyStored,Demand[i],energStorageMax)                         
               
            elif type_integration=="SL_L_P" or type_integration=="PL_E_PM" or type_integration=="SL_L_RF":
                #SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
                
                [T_out_K[i],Q_prod[i],T_in_K[i]]=offSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i])

            elif type_integration=="SL_S_FW" or type_integration=="SL_S_MW":
                #SL_S_FW Supply level with steam for solar heating of boiler feed water without storage 
                
                [T_out_K[i],Q_prod[i],T_in_K[i]]=offSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i])
                
            elif type_integration=="SL_S_FWS" or type_integration=="SL_S_MWS":
                #SL_S_FWS Supply level with steam for solar heating of boiler feed water with storage 
                
                [T_out_K[i],Q_prod[i],T_in_K[i],SOC[i]]=offStorageSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i],energStorageMax,energyStored)
                if Demand2[i]>0:
                    [Q_prod_lim[i],Q_prod[i],Q_discharg[i],Q_charg[i],energyStored,SOC[i],Q_defocus[i],Q_useful[i]]=outputStorageSimple(Q_prod[i],energyStored,Demand2[i],energStorageMax)                         
            
            elif type_integration=="SL_S_PD":
                #SL_S_PD Supply level with steam for direct steam generation
                
                [T_out_K[i],Q_prod[i],T_in_K[i]]=offSimple(fluidInput,bypass,T_in_flag,T_in_C_AR[i],temp[i])
    
    processDict={'T_in_flag':T_in_flag,'T_in_C_AR':T_in_C_AR.tolist(),'T_toProcess_C':T_toProcess_C.tolist()}
    
    # DataFRame summary of the simulation (only for SL_L_P)
#     simulationDF=pd.DataFrame({'DNI':DNI,'T_in':T_in_K-273,'T_out':T_out_K-273,'bypass':bypass,
#                               'Q_prod':Q_prod,'Q_prod_rec':Q_prod_rec,'flow_rate_kgs':flow_rate_kgs,
#                               'flow_rate_rec':flow_rate_rec,'Q_prod_lim':Q_prod_lim,'Demand':Demand,
#                               'Q_defocus':Q_defocus})

    #DataFRame summary of the simulation (only for SL_L_S)
    simulationDF=pd.DataFrame({'DNI':DNI,'Q_prod':Q_prod,'Q_charg':Q_charg,'Q_discharg':Q_discharg,'Q_defocus':Q_defocus,'Demand':Demand,'storage_energy':storage_energy,'SOC':SOC,'T_alm_K':T_alm_K-273})
        
    
    #%%
    # BLOCK 2.2 - ANUAL INTEGRATION <><><><><><><><><><><><><><><><><><><><><><><><><><><>
        
    Production_max=sum(Q_prod) #Produccion total en kWh. Asumiendo que se consume todo lo producido
    Production_lim=sum(Q_prod_lim) #Produccion limitada total en kWh
    Demand_anual=sum(Demand) #Demanda energética anual
    solar_fraction_max=100*Production_max/Demand_anual #Fracción solar maxima
    
    tonCo2Saved=Production_lim*co2factor #Tons of Co2 saved
    totalDischarged=(sum(Q_discharg))
#    totalCharged=(sum(Q_charg))
    Utilitation_ratio=100*((sum(Q_prod_lim))/(sum(Q_prod)))
    improvStorage=(100*sum(Q_prod_lim)/(sum(Q_prod_lim)-totalDischarged))-100 #Assuming discharged = Charged
    solar_fraction_lim=100*(sum(Q_prod_lim))/Demand_anual 
#    Energy_module_max=Production_max/num_modulos_tot
#    operation_hours=np.nonzero(Q_prod)
    DNI_anual_irradiation=sum(DNI)/1000 #kWh/year
#    Optic_rho_average=(sum(IAM)*rho_optic_0)/steps_sim
    Perd_term_anual=sum(Perd_termicas)/(1000) #kWh/year
    
    annualProdDict={'Q_prod':Q_prod.tolist(),'Q_prod_lim':Q_prod_lim.tolist(),'Demand':Demand.tolist(),'Q_charg':Q_charg.tolist(),
                    'Q_discharg':Q_discharg.tolist(),'Q_defocus':Q_defocus.tolist(),'solar_fraction_max':solar_fraction_max,
                    'solar_fraction_lim':solar_fraction_lim,'improvStorage':improvStorage,'Utilitation_ratio':Utilitation_ratio,
                    'flow_rate_kgs':flow_rate_kgs.tolist()}
    

#%%
# ------------------------------------------------------------------------------------
# BLOCK 3 - FINANCE SIMULATION -------------------------------------------------------
# ------------------------------------------------------------------------------------
    
    Break_cost=0 # Init variable
    if finance_study==1 and steps_sim==8759:#This eneters only for yearly simulations with the flag finance_study = 1

    # BLOCK 3.1 - PLANT INVESTMENT <><><><><><><><><><><><><><><><><><><><><><><><><><><>

        if origin==-2: #If ReSSSPI front-end is calling, then it uses Solatom propietary cost functions
            [Selling_price,Break_cost,OM_cost_year]=SOL_plant_costFunctions(num_modulos_tot,type_integration,almVolumen,fluidInput)

        elif origin==-3: #Use the CIMAV's costs functions
            destination=[Lat,Positional_longitude]
            [Selling_price,Break_cost,OM_cost_year]=CIMAV_plant_costFunctions(num_modulos_tot,type_integration,almVolumen,fluidInput,type_coll,destination) #Returns all the prices in mxn

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
            from Finance_modules.FinanceModels import Turn_key
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
            from Finance_modules.FinanceModels import ESCO
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
                 'IRR':IRR,'IRR10':IRR10,'tonCo2Saved':tonCo2Saved,'OM_cost_year':OMList}
    
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
              'outProcess_s':outProcess_s,'T_out_process_C':T_out_process_C,'P_op_bar':P_op_bar,
              'x_design':x_design,'h_in':h_in,'h_out':h_out,'hProcess_out':hProcess_out,'outProcess_h':outProcess_h,
              'Break_cost':Break_cost}
    
    # Plot functions
    
    # Plots for annual simulations
    if steps_sim==8759:
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
        if plots[15]==1: #(14) Plot Month savings
            output_excel2=savingsMonths(sender,origin,Q_prod_lim,Energy_Before,Fuel_price,Boiler_eff,lang,plotPath,imageQlty)

    
    # Plots for non-annual simulatios (With annual simuations you cannot see anything)
    if steps_sim!=8759:
        if plots[5]==1: #(5) Theta angle Plot
            thetaAnglesPlot(sender,origin,step_sim,steps_sim,theta_i_deg,theta_transv_deg,plotPath,imageQlty)
        if plots[6]==1: #(6) IAM angles Plot
            IAMAnglesPlot(sender,origin,step_sim,IAM_long,IAM_t,IAM,plotPath,imageQlty) 
        if plots[7]==1: #(7) Plot Overview (Demand vs Solar Radiation) 
            demandVsRadiation(sender,origin,lang,step_sim,Demand,Q_prod,Q_prod_lim,Q_prod_rec,steps_sim,DNI,plotPath,imageQlty)
        if plots[8]==1: #(8) Plot flowrates  & Temp & Prod
            flowRatesPlot(sender,origin,step_sim,steps_sim,flow_rate_kgs,flow_rate_rec,num_loops,flowDemand,flowToHx,flowToMix,m_dot_min_kgs,T_in_K,T_toProcess_C,T_out_K,T_alm_K,plotPath,imageQlty)
        if plots[9]==1: #(9)Plot Storage non-annual simulation  
            storageAnnual(sender,origin,SOC,Q_useful,Q_prod,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty)
             
    # Property plots
    if fluidInput=="water": #WATER
        if plots[10]==1: #(10) Mollier Plot for s-t for Water
            mollierPlotST(sender,origin,lang,type_integration,in_s,out_s,T_in_flag,T_in_C,T_in_C_AR,T_out_C,outProcess_s,T_out_process_C,P_op_bar,x_design,plotPath,imageQlty)              
        if plots[11]==1: #(11) Mollier Plot for s-h for Water 
            mollierPlotSH(sender,origin,lang,type_integration,h_in,h_out,hProcess_out,outProcess_h,in_s,out_s,T_in_flag,T_in_C,T_in_C_AR,T_out_C,outProcess_s,T_out_process_C,P_op_bar,x_design,plotPath,imageQlty)  
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
        productionSolar(sender,origin,lang,step_sim,DNI,m_dot_min_kgs,steps_sim,Demand,Q_prod,Q_prod_lim,Q_charg,Q_discharg,type_integration,plotPath,imageQlty)
       
    
#%%
# ------------------------------------------------------------------------------------
# BLOCK 5 - REPORT GENERATION ----------------------------------------------------------
# ------------------------------------------------------------------------------------
    
    # Create Report with results (www.ressspi.com uses a customized TEMPLATE called in the function "reportOutput"
    if steps_sim==8759: #The report is only available when annual simulation is performed
        if origin==-2:
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
            template_vars=reportOutput(origin,reportsVar,-1,"",pk,version,os.path.dirname(os.path.dirname(__file__))+'/ressspi',os.path.dirname(os.path.dirname(__file__)),Energy_Before_annual,sankeyDict)
        
        else:
            template_vars={} 
            reportsVar={'version':version,'logo_output':'no_logo','version':version,'type_integration':type_integration,
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
            if origin==0 or origin == -3:
                reportOutputOffline(reportsVar)
    else:
        template_vars={}
        reportsVar={}
        
    return(template_vars,plotVars,reportsVar,version)


# ----------------------------------- END SHIPcal -------------------------
# -------------------------------------------------------------------------
#%% 
       

# Variables needed for calling SHIPcal from terminal
    
#Plot Control ---------------------------------------
imageQlty=200

plots=[0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0] # Put 1 in the elements you want to plot. Example [1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0] will plot only plots #0, #8 and #9
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



finance_study=1

month_ini_sim=1
day_ini_sim=1
hour_ini_sim=1

month_fin_sim=12
day_fin_sim=31
hour_fin_sim=24



# -------------------- FINE TUNNING CONTROL ---------
mofINV=1 #Sobre el coste de inversion
mofDNI=1  #Corrección a fichero Meteonorm
mofProd=1 #Factor de seguridad a la producción de los módulos

# -------------------- SIZE OF THE PLANT ---------
num_loops=4 
n_coll_loop=20

#SL_L_P -> Supply level liquid parallel integration without storage
#SL_L_PS -> Supply level liquid parallel integration with storage
#SL_L_RF -> Supply level liquid return flow boost
#SL_S_FW -> Supply level solar steam for heating of boiler feed water without storage
#SL_S_FWS -> Supply level solar steam for heating of boiler feed water with storage
#SL_S_PD -> Supply level solar steam for direct solar steam generation 
#SL_L_S -> Storage
#SL_L_S3 -> Storage plus pasteurizator plus washing
type_integration="SL_S_MWS"
almVolumen=10000 #litros

# --------------------------------------------------
confReport={'lang':'spa','sender':'solatom','cabecera':'Resultados de la <br> simulación','mapama':0}
modificators={'mofINV':mofINV,'mofDNI':mofDNI,'mofProd':mofProd}
desginDict={'num_loops':num_loops,'n_coll_loop':n_coll_loop,'type_integration':type_integration,'almVolumen':almVolumen}
simControl={'finance_study':finance_study,'mes_ini_sim':month_ini_sim,'dia_ini_sim':day_ini_sim,'hora_ini_sim':hour_ini_sim,'mes_fin_sim':month_fin_sim,'dia_fin_sim':day_fin_sim,'hora_fin_sim':hour_fin_sim}    
# ---------------------------------------------------

origin=-2 #0 if new record; -2 if it comes from www.ressspi.com

if origin==0:
    #To perform simulations from command line using hardcoded inputs
    inputsDjango={}
    last_reg=666
else:
    #To perform simulations from command line using inputs like if they were from django
    inputsDjango= {'date': '2018-11-04', 'name': 'miguel', 'email': 'mfrasquetherraiz@gmail.com', 'industry': 'Example', 'sectorIndustry': 'Food_beverages', 'fuel': 'Gasoil-B', 'fuelPrice': 0.063, 'co2TonPrice': 0.0, 'co2factor': 0.00027, 'fuelUnit': 'eur_kWh', 'businessModel': 'turnkey', 'location': 'Sevilla', 'location_aux': '', 'surface': 1200, 'terrain': 'clean_ground', 'distance': 35, 'orientation': 'NS', 'inclination': 'flat', 'shadows': 'free', 'fluid': 'water', 'pressure': 6.0, 'pressureUnit': 'bar', 'tempIN': 80.0, 'tempOUT': 150.0, 'connection': 'storage', 'process': '', 'demand': 1500.0, 'demandUnit': 'MWh', 'hourINI': 8, 'hourEND': 18, 'Mond': 0.167, 'Tues': 0.167, 'Wend': 0.167, 'Thur': 0.167, 'Fri': 0.167, 'Sat': 0.167, 'Sun': 0.0, 'Jan': 0.083, 'Feb': 0.083, 'Mar': 0.083, 'Apr': 0.083, 'May': 0.083, 'Jun': 0.083, 'Jul': 0.083, 'Aug': 0.083, 'Sep': 0.083, 'Oct': 0.083, 'Nov': 0.083, 'Dec': 0.083, 'last_reg': 273}
    last_reg=inputsDjango['last_reg']
    

#[jSonResults,plotVars,reportsVar,version]=SHIPcal(origin,inputsDjango,plots,imageQlty,confReport,modificators,desginDict,simControl,last_reg)

