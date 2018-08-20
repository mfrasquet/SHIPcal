#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 19:54:51 2016

@author: Miguel Frasquet
"""
import sys
import os
#Import public paths
#sys.path.append('Solar_modules')
#sys.path.append('General_modules')
#sys.path.append('Integration_modules')
#sys.path.append('Plot_modules')

#sys.path.append('../TEMPLATE/Modules')
#sys.path.append('../Solatom_modules')

sys.path.append(os.path.dirname(os.path.dirname(__file__))+'/ressspi_solatom/')
#import time

from tkinter import Tk, messagebox
import numpy as np
import pandas as pd
import datetime


from General_modules.func_General import bar_MPa,MPa_bar,C_K,K_C,check_overwrite,DemandData,waterFromGrid,thermalOil

from Solar_modules.EQSolares import SolarData
from Solar_modules.EQSolares import theta_IAMs
from Solar_modules.EQSolares import IAM_calc

from General_modules.demandCreator_v1 import demandCreator

from iapws import IAPWS97

from Solatom_modules.solatom_param import solatom_param

from Integration_modules.integrations import *

from General_modules.fromDjangotoRessspi import djangoReport
from Solatom_modules.Solatom_finance import Turn_key,ESCO
from Solatom_modules.Solatom_finance import SP_plant_bymargin,SP_plant_bymargin2

from Solar_modules.iteration_process import flow_calc, flow_calcOil
from Solar_modules.iteration_process import IT_temp,IT_tempOil
from Plot_modules.plottingRessspi import *

from Solatom_modules.report import ressspiReport
from Solatom_modules.templateSolatom import reportOutput

def callDB(path):
   #Data base import
    columns=['version','date','name','mail','lang','industry','industrial_sector','fuel','business_model','fuel_price','fuel_unit','surface','distance','location','terrain','orientation','inclination','shadow','fluid','pression','pression_unit','process','Temp_out','Temp_in','scheme','consumption','unit_consumption','process_type','daily_consumpt','ini_hour','end_hour','batch_process','num_batch','dura_batch','week_consumpt','annual_consumpt','Mond','Tue','Wen','Thu','Fri','Sat','Sun','Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic','rebaja','correccionDNI','FS','num_loops','n_coll_loop','type_integration','almVolumen']
    data=pd.read_csv(path,sep=',',encoding = "ISO-8859-1")
    data= data.drop('Unnamed: 0', 1)
    return columns,data

def ressspiSIM(ressspiReg,data_reg,inputsDjango,inputFile,printReport,plots,imageQlty,confReport,modificators,desginDict,simControl,pk):
    #%%

    version="1.0.5" #Ressspi version
    type_coll=20 #Solatom 20" fresnel collector - Change if other collector is used
    
    pathRoot=os.path.dirname(os.path.dirname(__file__))  
#    Path(pathRoot).parent    
    
    path=os.path.dirname(os.path.dirname(__file__))+'/ressspi_solatom/database.csv' #DataBase SOLATOM 
    #path='DataBase/database.csv' #DataBase Genérica
    
    #pathFiles='/home/miguel/Desktop/Python_files/ressspiOffline/ressspiFiles/' #Files path SOLATOM
    pathFiles='ressspiFiles/' #FilePath genérico
    
    plotPath=pathRoot+'/ressspi/ressspiForm/static/results/' #FilePath genérico para imagenes
    
    
    columns,data=callDB(path)

    lang=confReport['lang']
    sender=confReport['sender']
    cabecera=confReport['cabecera']
    mapama=confReport['mapama']
    
    
    #Input Control ---------------------------------------
    
    mofINV=modificators['mofINV']
    mofDNI=modificators['mofDNI']
    mofProd=modificators['mofProd']
    

    num_loops=desginDict['num_loops']
    n_coll_loop=desginDict['n_coll_loop']
    type_integration=desginDict['type_integration']
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
    # ---------------------------------------------------------------------------------
    
    if ressspiReg==-2: 
        [inputs,annualConsumptionkWh,reg,P_op_bar,monthArray,weekArray,dayArray]=djangoReport(inputsDjango)
        
        file_demand=demandCreator(annualConsumptionkWh,dayArray,weekArray,monthArray)
        
        fileName="results"+str(reg)
        
        
        annualConsumptionkWh=annualConsumptionkWh
        arraysConsumption={'dayArray':dayArray,'weekArray':weekArray,'monthArray':monthArray}
        inputs.update(arraysConsumption)
        
              
        fluidInput=inputs['fluid'] #Type of fluid 
        T_in_C=inputs['inletTemp'] #Temperatura baja
        T_out_C=inputs['outletTemp'] #Temperatura alta
        P_op_bar=P_op_bar
        
        typeScheme=inputs['connectProcess'] #Tipo de integración
    
        
        #I get the price and I adjust it depending the unit
        fuelPriceUnit=inputs['priceUnit']
        co2TonPrice=inputs['co2TonPrice']
        fuel=inputs['currentFuel']
         
        priceFactor=1
        if fuel=="Gas Natural" or fuel=="GNL" or fuel=="Natural gas" or fuel=="LNG" or fuel=="NG":
            co2factor=.2016/1000 #TonCo2/kWh     
            if fuelPriceUnit=="eur/m3":
                priceFactor=1/9.02 #http://petromercado.com/blog/37-articulos/182-poder-calorifico-en-kw-del-gasoleo-c-butano-y-pellet.html
        
        if fuel=="Gasoil" or fuel=="Fueloil" or fuel=='Gasoil-C' or fuel=='Gasoil-B' or fuel=='Fueloil1' or fuel=='Fueloil2' or fuel=='Fueloil3':
            co2factor=.27/1000 #TonCo2/kWh          
            if fuelPriceUnit=="eur/litro":
                priceFactor=1/10.18 #http://petromercado.com/blog/37-articulos/182-poder-calorifico-en-kw-del-gasoleo-c-butano-y-pellet.html
        
        if fuel=="Electricidad" or fuel=="Electricity":
            co2factor=.385/1000 #TonCo2/kWh  
        
        if fuel=="Otro" or fuel=="Other" or fuel=="Air-propane" or fuel=="Butane" or fuel=="Propane" or fuel=="Biomass":
            co2factor=.385/1000 #TonCo2/kWh
            if fuelPriceUnit=="eur/litro":
                priceFactor=1/10.18 #http://petromercado.com/blog/37-articulos/182-poder-calorifico-en-kw-del-gasoleo-c-butano-y-pellet.html
    
        
        businessModel=inputs['businessModel']      #Modelo de negocio seleccionado                               
        Fuel_price=inputs['fuelPrice']*priceFactor   #Price of fossil fuel in €/kWh
         
        #Meteo
        meteoDB = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/meteoDB.csv", sep=',') 
        
        locationFromRessspi=inputs['location']
        localMeteo=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'meteoFile'].iloc[0]
        file_loc=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/"+localMeteo 
        Lat=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'Latitud'].iloc[0]
        Huso=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'Huso'].iloc[0]
        
        

    if ressspiReg==-1:
         [inputs,file_demand,annualConsumptionkWh,last_reg]=ressspiReport(1,inputFile,path,pathFiles,version)
         ressspiReg=1
         columns,data=callDB(path)
         data_reg=len(data)-1

            
    if ressspiReg==0:  
        # --------------------------DATA ORIGIN FROM SPECIFIC SIMULATION
        company="Almendra"
        nameUser="UNEX"
        emailUser=""
        sectorUser="Almendra"
        localInput="Badajoz" #Tiene que corresponder a la columna Provincia de meteoDB
        surfaceAvailable=1000
        orientation="NE-SO"
        inclination="plano"
        shadowInput="Sin sombra"
        distanceInput=15
        terreno="Terreno"
        mainProcessInput="Desconocido"
        perfilDiarioTipo="continuo"
        perfilDiario="continuo"
        ini_hour=0
        end_hour=0
        batch_process='sin_datos'
        num_batch='nan'
        dura_batch='nan'
        perfilSemanal="Toda la semana"
        perfilAnual="continuo"    
    #    dayArray=[0.0400,0.0464,0.0480,0.0480,0.0480,0.0520,0.0560,0.0650,0.0840,0.0654,0.0456,0.0340,0.0260,0.0180,0.0180,0.0190,0.0240,0.0280,0.0374,0.0452,0.0470,0.0374,0.0336,0.0340] #hotel
    #    dayArray=[0,0,0,0,0,0,0,0,1/8,1/8,1/8,1/8,1/8,1/8,1/8,1/8,0,0,0,0,0,0,0,0] #Constante 8 h day
        dayArray=[0,0,0,0,0,0,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,0,0,0,0,0,0] #Constante 12 h day
    #    dayArray=[0,0,0,0,0,0,1/7,1/7,1/7,1/7,1/7,1/7,1/7,0,0,0,0,0,0,0,0,0,0,0] #Constante 6 h day
    #    dayArray=[0,0,0,0,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,1/18,0,0]
    #    dayArray=[0,0,0,0,1/16,1/16,1/16,1/16,1/16,1/16,1/16,1/16,1/16,1/16,1/16,1/16,1/16,1/16,1/16,1/16,0,0,0,0] #Constante 8 h day
    #    dayArray=[1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24,1/24] #Constante 
    #    dayArray=[0,0,0,0,0,0,0,0,0,0,0.25,0.25,0.25,0.25,0,0,0,0,0,0,0,0,0,0] #Constante 4 h day
        weekArray=[0.2,0.2,0.2,0.2,0.2,0,0] #Sin findes
    #    weekArray=[1/6,1/6,1/6,1/6,1/6,1/6,0] #Sin un día
    #    weekArray=[1/7,1/7,1/7,1/7,1/7,1/7,1/7] #Constante
    #    weekArray=[0.12,0.12,0.12,0.12,0.12,0.2,0.2]
    
    #    weekArray=[0.0989404709,0.1685324774,0.1334964808	,0.1486023508,0.1484373844,0.1447645084,0.1572263273]
        
    #    monthArray=[1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12,1/12] #Constante
        monthArray=[0,0,1/10,1/10,1/10,1/10,1/10,1/10,1/10,1/10,1/10,1/10] #Almendra
    #    monthArray=[0.0848,0.0925,0.0838,0.0780,0.1080,0.0750,0.0599,0.0752,0.0780,0.0873,0.0925,0.0848] #Chemical factory
    #    monthArray=[0.05,0.05,0.05,0.0875,0.0875,0.1125,0.1125,0.1125,0.1125,0.0875,0.0875,0.05] #Laundry
    #    monthArray=[0.1889825061,0.1380203965,0.1184212922,0.0627569903,0.0532994342,0.0367279314,0.030371343,0.0260940786,0.0386296228,0.0487369151,0.1126647324,0.1452947574]
    #    monthArray=[0.0748913733,0.0784088129,0.0891306615,0.0831238069,0.0821990364,0.0806866629,0.0894832435,0.0949372728,0.0852327818,0.0849441664,0.0794752549,0.0774869267]
    #    monthArray=[0.0476047652,0.0694529061,0.0638385618,0.0505572166,0.0481952555,0.1324291646,0.1579514673,0.1679241923,0.1425237368,0.0439118576,0.033911014,0.0416998622]
    #    monthArray=[0.077938362,0.0669174421,0.1026199432,0.0837457929,0.0787302844,0.1045337557,0.0886953079,0.0917310104,0.0910050815,0.0692272157,0.0669174421,0.077938362]
    #    monthArray=[0.09433962264,0.09433962264,0.09433962264,0.09433962264,0.09433962264,0.07547169811,0.07547169811,0.07547169811,0.07547169811,0.07547169811,0.07547169811,0.07547169811]
        totalConsumption=190000 #kWh
        energyConsumptionUnits='kWh'
        
        fluidInput="vapor" #"Agua sobrecalentada" "vapor" "Aceite térmico" 
        typeScheme="directo" #"directo" "acum" #Solo texto No vinculante
        T_out_C=180 #Temperatura alta
        T_in_C=90 #Temperatura baja
        P_op_bar=8 #bar 
        pressureUnit='bar'
        
    
        
        fileName="results_"+company 
        businessModel="Llave en mano"
        fuel="Gasoil" #Gas Natural, GNL, Gasoil, Electricidad
        Fuel_price=0.05 #Price of fossil fuel in €/kWh
        co2TonPrice=7.5 #(€/TonCo2 emitida)
        priceUnit='€/kWh'
        #Localizacion
         #Meteo
        localMeteo="Badajoz.dat"
        meteoDB = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/meteoDB.csv", sep=',') 
        file_loc=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/"+localMeteo   
       
        Lat=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Latitud'].iloc[0]
        Huso=meteoDB.loc[meteoDB['meteoFile'] == localMeteo, 'Huso'].iloc[0]
    
        # -------------------------------------------------
        #Obtencion de archivos demand   
        #La demanda se mete con un csv horario anual en kW 
        file_demand=demandCreator(totalConsumption,dayArray,weekArray,monthArray)
    #    file_demand="/home/miguel/Desktop/Python_files/PLAT_VIRT/fresnel/Demand_files/T3Hospitality.csv"
        
        if fuel=="Gas Natural" or fuel=="GNL" or fuel=="Natural gas" or fuel=="LNG":
            co2factor=.2016/1000 #TonCo2/kWh
        if fuel=="Gasoil" or fuel=="Fueloil":
            co2factor=.27/1000 #TonCo2/kWh
        if fuel=="Electricidad" or fuel=="Electricity":
            co2factor=.385/1000 #TonCo2/kWh
          
    
        new_data={len(data) : [version,datetime.datetime.now().strftime("%d-%m-%y"),nameUser,emailUser,'Spanish',company,sectorUser,fuel,businessModel,Fuel_price,'eur/kWh',surfaceAvailable,distanceInput,localInput,terreno,orientation,inclination,shadowInput,fluidInput,P_op_bar,'bar',mainProcessInput,T_out_C,T_in_C,typeScheme,totalConsumption,'kWh',perfilDiarioTipo,dayArray,ini_hour,end_hour,batch_process,num_batch,dura_batch,perfilSemanal,perfilAnual,weekArray[0],weekArray[1],weekArray[2],weekArray[3],weekArray[4],weekArray[5],weekArray[6],monthArray[0],monthArray[1],monthArray[2],monthArray[3],monthArray[4],monthArray[5],monthArray[6],monthArray[7],monthArray[8],monthArray[9],monthArray[10],monthArray[11],1.0001,1,1.001,1,1,'SL_L_P',0]}
        new_data = pd.DataFrame.from_dict(new_data, orient='index')
        new_data.columns = columns
        data=data.append(new_data, ignore_index=True)
        data.to_csv(path, sep=',',encoding = "ISO-8859-1")
        reg=len(data)-1
        
        inputs = {"date":datetime.datetime.now().strftime("%d-%m-%y"), "nameUser" :nameUser,"companyName": company,
            "emailUser" :emailUser,"sectorUser":sectorUser,"currentFuel":fuel,"fuelPrice":Fuel_price,"co2TonPrice":co2TonPrice,"priceUnit":priceUnit,"businessModel":businessModel, "location":localMeteo,
            "surfaceAvailable":surfaceAvailable,"terrainType": terreno,"orientation":orientation,"inclination":inclination,  "shadow":shadowInput,   "distance":distanceInput, "mainProcess":mainProcessInput,
            "fluid":fluidInput, "pressure":P_op_bar,"pressureUnit":pressureUnit,  "connectProcess":typeScheme,  "outletTemp":T_out_C,  "inletTemp":T_in_C,
            "energyConsumption":totalConsumption,"energyConsumptionUnits":energyConsumptionUnits,"typeProcessDay":perfilDiarioTipo,"dayProfile":perfilDiario,  "weekProfile":perfilSemanal,         
            "annualProfile":perfilAnual,'localInput':localInput,'dayArray':dayArray,'weekArray':weekArray,'monthArray':monthArray}
            


    # --------------------------------------------------------------------------------------
    if ressspiReg==1:        
        new=0
        reg=data_reg
        flags=['rebaja','num_loops','n_coll_loop','type_integration','almVolumen','correccionDNI','FS']
        flagsValue=[mofINV,num_loops,n_coll_loop,type_integration,almVolumen,mofDNI,mofProd]
        flagsValuesOld=[data.at[reg,'rebaja'],data.at[reg,'num_loops'],data.at[reg,'n_coll_loop'] ,data.at[reg,'type_integration'],data.at[reg,'almVolumen'],data.at[reg,'correccionDNI'],data.at[reg,'FS']]
        flagOverwrite=check_overwrite(data,reg,mofINV,num_loops,n_coll_loop,type_integration,almVolumen,mofDNI,mofProd)
        if any(t==True for t in flagOverwrite):
            root = Tk()
            result=messagebox.askyesno("Vas a sobre-escribir un registro de la base de datos","Estas simulando el fichero "+str(reg)+" de "+str(data['industry'][reg])+". Vas a sobrescribir estos parámetros: "+str(np.array(flags)[np.array(flagOverwrite)])+", con valor "+str(np.array(flagsValuesOld)[np.array(flagOverwrite)])+" por los nuevos valores "+str(np.array(flagsValue)[np.array(flagOverwrite)])+". Quieres continuar?")
            
            if result==False:
                root.destroy()
                sys.exit()
            else:
                pass
            root.destroy()
            
        fileName="results"+str(reg)
        
        inputs = {"date":data['date'][reg], "nameUser" :data['name'][reg],"companyName": data['industry'][reg],
            "emailUser" :data['mail'][reg],"sectorUser":data['industrial_sector'][reg],"currentFuel":data['fuel'][reg],"fuelPrice":data['fuel_price'][reg],"priceUnit":data['fuel_unit'][reg],"businessModel":data['business_model'][reg], "location":data['location'][reg],
            "surfaceAvailable":data['surface'][reg],"terrainType": data['terrain'][reg],"orientation":data['orientation'][reg],"inclination":data['inclination'][reg],  "shadow":data['shadow'][reg],"distance":data['distance'][reg],"mainProcess":data['process'][reg],
            "fluid":data['fluid'][reg], "pressure":data['pression'][reg],"pressureUnit":data['pression_unit'][reg],  "connectProcess":data['scheme'][reg],  "outletTemp":data['Temp_out'][reg],  "inletTemp":data['Temp_in'][reg],
            "energyConsumption":data['consumption'][reg],"energyConsumptionUnits":data['unit_consumption'][reg],"typeProcessDay":data['process_type'][reg],"dayProfile":data['daily_consumpt'][reg],  "weekProfile":data['week_consumpt'][reg],         
            "annualProfile":data['annual_consumpt'][reg],'localInput':data['location'][reg]}
            
        
        annualConsumptionkWh=data['consumption'][reg]
        dayArray=[float(s) for s in data['daily_consumpt'][reg][1:-1].split(',')]
        weekArray=[float(data['Mond'][reg]),float(data['Tue'][reg]),float(data['Wen'][reg]),float(data['Thu'][reg]),float(data['Fri'][reg]),float(data['Sat'][reg]),float(data['Sun'][reg])]
        monthArray=[float(data['Ene'][reg]),float(data['Feb'][reg]),float(data['Mar'][reg]),float(data['Abr'][reg]),float(data['May'][reg]),float(data['Jun'][reg]),float(data['Jul'][reg]),float(data['Ago'][reg]),float(data['Sep'][reg]),float(data['Oct'][reg]),float(data['Nov'][reg]),float(data['Dic'][reg])]
        arraysConsumption={'dayArray':dayArray,'weekArray':weekArray,'monthArray':monthArray}
        inputs.update(arraysConsumption)
        
        
        
        file_demand=demandCreator(annualConsumptionkWh,dayArray,weekArray,monthArray)
        
        fluidInput=data['fluid'][reg] #Type of fluid 
        T_in_C=data['Temp_in'][reg] #Temperatura baja
        T_out_C=data['Temp_out'][reg] #Temperatura alta
        P_op_bar=data['pression'][reg]
        
        typeScheme=data['scheme'][reg] #Tipo de integración
    
        
        #I get the price and I adjust it depending the unit
        fuelPriceUnit=data['fuel_unit'][reg]
        fuel=data['fuel'][reg]
         
        priceFactor=1
        if fuel=="Gas Natural" or fuel=="GNL" or fuel=="Natural gas" or fuel=="LNG":
            co2factor=.2016/1000 #TonCo2/kWh     
            if fuelPriceUnit=="eur/m3":
                priceFactor=1/9.02 #http://petromercado.com/blog/37-articulos/182-poder-calorifico-en-kw-del-gasoleo-c-butano-y-pellet.html
        
        if fuel=="Gasoil" or fuel=="Fueloil":
            co2factor=.27/1000 #TonCo2/kWh          
            if fuelPriceUnit=="eur/litro":
                priceFactor=1/10.18 #http://petromercado.com/blog/37-articulos/182-poder-calorifico-en-kw-del-gasoleo-c-butano-y-pellet.html
        
        if fuel=="Electricidad" or fuel=="Electricity":
            co2factor=.385/1000 #TonCo2/kWh  
        
        if fuel=="Otro" or fuel=="Other":
            co2factor=.385/1000 #TonCo2/kWh
            if fuelPriceUnit=="eur/litro":
                priceFactor=1/10.18 #http://petromercado.com/blog/37-articulos/182-poder-calorifico-en-kw-del-gasoleo-c-butano-y-pellet.html
    
        
        businessModel=data['business_model'][reg]      #Modelo de negocio seleccionado                               
        Fuel_price=data['fuel_price'][reg]*priceFactor   #Price of fossil fuel in €/kWh
        co2TonPrice=0 #(€/TonCo2 emitida)
         
        #Meteo
        meteoDB = pd.read_csv(os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/meteoDB.csv", sep=',') 
        
        locationFromRessspi=data['location'][reg]
        localMeteo=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'meteoFile'].iloc[0]
        file_loc=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/METEO/"+localMeteo  
        Lat=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'Latitud'].iloc[0]
        Huso=meteoDB.loc[meteoDB['Provincia'] == locationFromRessspi, 'Huso'].iloc[0]
    
         #%%
    
    
    
    if ressspiReg>-2:
        data.at[reg,'num_loops'] = num_loops
        data.at[reg,'n_coll_loop'] = n_coll_loop
        data.at[reg,'type_integration'] = type_integration
        data.at[reg,'almVolumen'] = almVolumen
        data.at[reg,'rebaja'] = mofINV
        data.at[reg,'correccionDNI'] = mofDNI
        data.at[reg,'FS'] = mofProd
        
        
        data.to_csv(path, sep=',',encoding = "ISO-8859-1")
        
    # -----------------------------------------------
    
    #Colector
    beta=0
    orient_az_rad=0
    IAM_file='Solatom.csv'
    IAM_folder=os.path.dirname(os.path.dirname(__file__))+"/ressspi_solatom/IAM_files/"  
    IAMfile_loc=IAM_folder+IAM_file
    
    
    REC_type=1
    D,Area_coll,rho_optic_0,huella_coll,Long,Apert_coll=solatom_param(type_coll)
    Area=Area_coll*n_coll_loop #Area de loop
    Area_total=Area*num_loops #Area total de apertura
    
    #Process control
    T_in_C_AR_mes=np.array([8,9,11,13,14,15,16,15,14,13,11,8]) #Array con las temperaturas mensuales de agua de red
    T_in_C_AR=waterFromGrid(T_in_C_AR_mes)
    #Process parameters
    lim_inf_DNI=200
    m_dot_min_kgs=0.08
    coef_flow_rec=2
    
    
    
    # ---------------------------------------------------------------------
    # --------------------------- SIMULATION ------------------------------
    # ---------------------------------------------------------------------
      
        
    num_modulos_tot=n_coll_loop*num_loops
    
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
    
    if type_integration=="SL_L_RF":
        sat_liq=0 #Not used
        sat_vap=0 #Not used
        x_design=0 #Not used
        outProcess_h=0 #Not used
        almVolumen=0 #litros Not used
        energStorageMax=0 #kWh
        energyStored=0 #kWh
        porctSensible=0 #Not used
        
        
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
        sat_liq=0 #Not used
        sat_vap=0 #Not used
        x_design=0 #Not used
        outProcess_h=0 #Not used
        porctSensible=0 #Not used
        T_out_HX_C=0 #ot used
    
        
        P_op_Mpa=P_op_bar/10
        almVolumen=0 #litros
        energStorageMax=0 #kWh
        energyStored=0 #kWh
        
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
        sat_liq=0 #Not used
        sat_vap=0 #Not used
        x_design=0 #Not used
        outProcess_h=0 #Not used
        porctSensible=0 #Not used
        T_out_HX_C=0 #ot used
        T_out_process_C=0 #Not used
        T_in_process_C=0 #Not used
        outProcess_s=0 #Not used
        hProcess_out=0 #Not used
        
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
        sat_liq=0 #Not used
        sat_vap=0 #Not used
        x_design=0 #Not used
        outProcess_h=0 #Not used
        porctSensible=0 #Not used
        T_out_process_C=0 #Not used
        T_in_process_C=0 #Not used
        T_out_HX_C=0 #ot used
        outProcess_s=0 #Not used
        hProcess_out=0 #Not used
        
        
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
        x_design=0 #Not used
        outProcess_h=0 #Not used
        T_out_process_C=0 #Not used
        T_in_process_C=0 #Not used
        T_out_HX_C=0 #Not used
        outProcess_s=0 #Not used
        hProcess_out=0 #Not used
        
        P_op_Mpa=P_op_bar/10
        almVolumen=0 #litros
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
        T_out_process_C=0 #Not used
        T_in_process_C=0 #Not used
        T_out_HX_C=0 #Not used
        x_design=0 #Not used
        outProcess_h=0 #Not used
        outProcess_s=0 #Not used
        hProcess_out=0 #Not used
        
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
            sankeyDict=SankeyPlot(ressspiReg,lang,Production_max,Production_lim,Perd_term_anual,DNI_anual_irradiation,Area,num_loops,imageQlty,plotPath)
        if plots[0]==0: #(0) Sankey plot -> no plotting
            sankeyDict={'Production':0,'raw_potential':0,'Thermal_loss':0,'Utilization':0}
        if plots[1]==1: #(1) Production week Winter & Summer
            prodWinterPlot(ressspiReg,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty)   
            prodSummerPlot(ressspiReg,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty)  
        if plots[2]==1 and finance_study==1: #(2) Plot Finance
            financePlot(ressspiReg,lang,n_years_sim,Acum_FCF,FCF,m_dot_min_kgs,steps_sim,AmortYear,Selling_price,plotPath,imageQlty)
        if plots[3]==1: #(3)Plot of Storage first week winter & summer 
            storageWinter(ressspiReg,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty)    
            storageSummer(ressspiReg,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty)    
        if plots[4]==1: #(4) Plot Prod months
            output_excel=prodMonths(ressspiReg,Q_prod,Q_prod_lim,DNI,Demand,lang,plotPath,imageQlty)
    
    # Non-annual simulatios (With annual simuations you cannot see anything)
    if steps_sim!=8759:
        if plots[5]==1: #(5) Theta angle Plot
            thetaAnglesPlot(ressspiReg,step_sim,steps_sim,theta_i_deg,theta_transv_deg,plotPath,imageQlty)
        if plots[6]==1: #(6) IAM angles Plot
            IAMAnglesPlot(ressspiReg,step_sim,IAM_long,IAM_t,IAM,plotPath,imageQlty) 
        if plots[7]==1: #(7) Plot Overview (Demand vs Solar Radiation) 
            demandVsRadiation(ressspiReg,lang,step_sim,Demand,Q_prod,Q_prod_lim,Q_prod_rec,steps_sim,DNI,plotPath,imageQlty)
        if plots[8]==1: #(8) Plot flowrates  & Temp & Prod
            flowRatesPlot(ressspiReg,step_sim,steps_sim,flow_rate_kgs,flow_rate_rec,num_loops,flowDemand,flowToHx,flowToMix,m_dot_min_kgs,T_in_K,T_toProcess_C,T_out_K,T_alm_K,plotPath,imageQlty)
        if plots[9]==1: #(9)Plot Storage non-annual simulation  
            storageAnnual(ressspiReg,SOC,Q_useful,Q_prod,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty)
             
    # Property plots
    if fluidInput!="oil": #WATER
        if plots[10]==1: #(10) Mollier Plot for s-t for Water
            mollierPlotST(ressspiReg,lang,type_integration,in_s,out_s,T_in_flag,T_in_C,T_in_C_AR,T_out_C,outProcess_s,T_out_process_C,P_op_bar,x_design,plotPath,imageQlty)              
        if plots[11]==1: #(11) Mollier Plot for s-h for Water 
            mollierPlotSH(ressspiReg,lang,type_integration,h_in,h_out,hProcess_out,outProcess_h,in_s,out_s,T_in_flag,T_in_C,T_in_C_AR,T_out_C,outProcess_s,T_out_process_C,P_op_bar,x_design,plotPath,imageQlty)  
    if fluidInput=="oil": 
        if plots[12]==1:
            rhoTempPlotOil(ressspiReg,lang,T_out_C,plotPath,imageQlty) #(12) Plot thermal oil properties Rho & Cp vs Temp
        if plots[13]==1:
            viscTempPlotOil(ressspiReg,lang,T_out_C,plotPath,imageQlty) #(13) Plot thermal oil properties Viscosities vs Temp        
    
    # Other plots
    if plots[14]==1: #(14) Plot Production
        productionSolar(ressspiReg,lang,step_sim,DNI,m_dot_min_kgs,steps_sim,Demand,Q_prod,Q_prod_lim,Q_charg,Q_discharg,type_integration,plotPath,imageQlty)
    
    
    #%% 
    if steps_sim==8759:
        reportsVar={'date':inputs['date'],'type_integration':type_integration,
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

        if ressspiReg==-2: 
            data=""
        template_vars=reportOutput(ressspiReg,reg,reportsVar,inputs,data,printReport,pk,version,(os.path.dirname(__file__)))
    else:
        template_vars={}
        reportsVar={}
        
    return(template_vars,plotVars,reportsVar,version)

# ----------------------------------- END RESSSPI -------------------------
# -------------------------------------------------------------------------
    #%% 
    
    
#lang="spa"
lang="spa"
#sender="generico"
sender="solatom"
#sender="ressspi"
#cabecera="Estudio preliminar"
cabecera="Resultados de la <br> simulación"
#cabecera="Simulation results"
mapama=0 #mapama=1 generates a mapama image
    
    
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



data_reg=74
inputsDjango={}
inputFile=1 #For reading directly from file
ressspiReg=1 #0 if new record #1 if it's already in the database #-1 if it comes from a text file #-2 if it comes from django

printReport=1


# -------------------- FINE TUNNING CONTROL ---------
mofINV=1.6 #Sobre el coste de inversion
mofDNI=1  #Corrección a fichero Meteonorm
mofProd=.9 #Factor de seguridad a la producción de los módulos

# -------------------- TAMAÑO INSTALACION ---------
num_loops=6   
n_coll_loop=8

#SL_L_P -> Supply level liquid parallel integration without storage
#SL_L_PS -> Supply level liquid parallel integration with storage
#SL_L_RF -> Supply level liquid return flow boost
#SL_S_FW -> Supply level solar steam for heating of boiler feed water without storage
#SL_S_FWS -> Supply level solar steam for heating of boiler feed water with storage
#SL_S_PD -> Supply level solar steam for direct solar steam generation 
#SL_L_S -> Storage
#SL_L_S3 -> Storage plus pasteurizator plus washing
type_integration="SL_S_PD"
almVolumen=5000 #litros

# --------------------------------------------------
confReport={'lang':lang,'sender':sender,'cabecera':cabecera,'mapama':mapama}
modificators={'mofINV':mofINV,'mofDNI':mofDNI,'mofProd':mofProd}
desginDict={'num_loops':num_loops,'n_coll_loop':n_coll_loop,'type_integration':type_integration,'almVolumen':almVolumen}
simControl={'finance_study':finance_study,'mes_ini_sim':mes_ini_sim,'dia_ini_sim':dia_ini_sim,'hora_ini_sim':hora_ini_sim,'mes_fin_sim':mes_fin_sim,'dia_fin_sim':dia_fin_sim,'hora_fin_sim':hora_fin_sim}    
# ---------------------------------------------------

inputsDjango={'date': '2018-08-06', 'name': 'miguel', 'email': 'miguel.frasquet@solatom.com', 'industry': 'Deretil 2', 'sectorIndustry': 'Chemical', 'fuel': 'NG', 'fuelPrice': 0.03, 'co2TonPrice': 0.0, 'fuelUnit': 'eur_kWh', 'businessModel': 'turnkey', 'location': 'Almeria', 'location_aux': '', 'surface': 400, 'terrain': 'rooftop_sandwich', 'distance': 400, 'orientation': 'NS', 'inclination': 'soft-tilt', 'shadows': 'free', 'fluid': 'steam', 'pressure': 7.5, 'pressureUnit': 'bar', 'tempIN': 80.0, 'tempOUT': 125.0, 'connection': 'process', 'process': '', 'demand': 78699261.0, 'demandUnit': 'kWh', 'hourINI': '1', 'hourEND': '24', 'Mond': 0.14285714285714285, 'Tues': 0.14285714285714285, 'Wend': 0.14285714285714285, 'Thur': 0.14285714285714285, 'Fri': 0.14285714285714285, 'Sat': 0.14285714285714285, 'Sun': 0.14285714285714285, 'Jan': 0.08333333333333333, 'Feb': 0.08333333333333333, 'Mar': 0.08333333333333333, 'Apr': 0.08333333333333333, 'May': 0.08333333333333333, 'Jun': 0.08333333333333333, 'Jul': 0.08333333333333333, 'Aug': 0.08333333333333333, 'Sep': 0.08333333333333333, 'Oct': 0.08333333333333333, 'Nov': 0.08333333333333333, 'Dec': 0.08333333333333333, 'last_reg': 81}


#[template_vars,plotVars,reportsVar,version]=ressspiSIM(ressspiReg,data_reg,inputsDjango,inputFile,printReport,plots,imageQlty,confReport,modificators,desginDict,simControl,inputsDjango['last_reg'])
