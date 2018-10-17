# -*- coding: utf-8 -*-
"""
Integration schemes from task 49
Created on Sat May  5 20:06:05 2018

version: 1.0



@author: miguel frasquet (SOLATOM)
"""

from iapws import IAPWS97
import numpy as np
from Solar_modules.iteration_process import flow_calc, flow_calcOil
from Solar_modules.iteration_process import IT_temp,IT_tempOil
from General_modules.func_General import thermalOil
from General_modules.func_General import bar_MPa,MPa_bar,C_K,K_C

def offWaterSimple(bypass,T_in_flag,T_in_C_AR,T_in_K_old):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52             
    bypass.append("OFF")
    if T_in_flag==1:
        T_in_K=T_in_K_old
    else:
        T_in_K=T_in_C_AR+273
    T_out_K=0+273
    Q_prod=0 #No hay produccion  
    return [T_out_K,Q_prod,T_in_K]

def offOilSimple(bypass,T_in_K_old):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52             
    bypass.append("OFF")
    T_in_K=T_in_K_old
    T_out_K=0+273
    Q_prod=0 #No hay produccion  
    return [T_out_K,Q_prod,T_in_K]

def offStorageWaterSimple(bypass,T_in_flag,T_in_C_AR,T_in_K_old,energStorageMax,energyStored):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52             
    bypass.append("OFF")
    if T_in_flag==1:
        T_in_K=T_in_K_old
    else:
        T_in_K=T_in_C_AR+273
    T_out_K=0+273
    Q_prod=0 #No hay produccion
    SOC=100*energyStored/energStorageMax
    return [T_out_K,Q_prod,T_in_K,SOC]
def offOnlyStorageWaterSimple(T_in_K_old,energStorageMax,energyStored,T_K_alm_old,storage_energy_old):

    T_in_K=T_in_K_old

    T_out_K=0+273
    Q_prod=0 #No hay produccion
#    SOC=100*(T_K_alm_old-273)/(T_max_storage-273)
    SOC=100*energyStored/energStorageMax
    storage_energy=storage_energy_old
    T_alm_K=T_K_alm_old
    return [T_out_K,Q_prod,T_in_K,SOC,T_alm_K,storage_energy]
def inputsWithDNIWaterSimple(T_in_flag,T_in_K_old,T_in_C_AR,T_out_K_old,T_in_C,P_op_Mpa,bypass_old):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 

    if T_in_flag==1:
        if bypass_old=="REC" and T_out_K_old>(T_in_C+273):
            T_in_K=T_out_K_old
        else:
            T_in_K=T_in_C+273
    else:
        if bypass_old=="REC" and T_out_K_old>(T_in_C_AR+273):
            T_in_K=T_out_K_old
        else:
            T_in_K=T_in_C_AR+273
        
    inlet=IAPWS97(P=P_op_Mpa, T=T_in_K)
    h_in_kJkg=inlet.h
    return [h_in_kJkg,T_in_K]
def inputsWithDNIOilSimple(T_in_K_old,T_out_K_old,T_in_C,bypass_old):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 

    if bypass_old=="REC" and T_out_K_old>(T_in_C+273):
        T_in_K=T_out_K_old
    else:
        T_in_K=T_in_C+273

    return [T_in_K]
def operationOilKettleSimple(bypass,T_in_K_old,T_out_K_old,T_in_C,P_op_Mpa,bypass_old,T_out_C,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0,num_loops,FS,coef_flow_rec,m_dot_min_kgs,Q_prod_rec_old,T_alm_K,DeltaKettle):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52    
    [T_in_K]=inputsWithDNIOilSimple(T_in_K_old,T_out_K_old,T_in_C,bypass_old)    
    #Calculo el flowrate necesario para poder dar el salto de temp necesario
    T_out_K=T_out_C+273
    T_av_K=(T_in_K+T_out_K)/2
    [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
    
    flow_rate_kgs=1 #kg/s
    T_out_K,Perd_termicas=IT_tempOil(T_in_K,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_kgs,rho_optic_0)

    if T_out_K<T_alm_K+DeltaKettle:
        #RECIRCULACION
        flow_rate_rec=flow_rate_kgs
        T_out_K,Perd_termicas=IT_tempOil(T_in_K,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_rec,rho_optic_0)    
        Q_prod=0 #No hay produccion
        
        T_av_K=(T_in_K+T_out_K)/2
        [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
        
        Q_prod_rec=flow_rate_rec*Cp_av*(T_out_K-T_in_K)
        bypass.append("REC")
        newBypass="REC"
    else:
        #PRODUCCION
        if bypass_old=="REC":
            if Q_prod_rec_old>0:
                Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS+Q_prod_rec_old*FS #In kWh
            else:
                Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS#In kWh
        else:
            Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS #In kW
        flow_rate_rec=0
        Q_prod_rec=0
        bypass.append("PROD")
        newBypass="PROD"
    return [T_out_K,flow_rate_kgs,Perd_termicas,Q_prod,T_in_K,flow_rate_rec,Q_prod_rec,newBypass]
    
def operationOnlyStorageWaterSimple(T_max_storage,T_in_K_old,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0,num_loops,FS,flow_rate_kgs):
#SL_L_S Supply level with liquid heat transfer media just for heat a storage
    inlet=IAPWS97(P=P_op_Mpa, T=T_in_K_old)
    h_in_kJkg=inlet.h
    
#    gainSolar=DNI*Area*IAM*rho_optic_0
    T_out_K,Perd_termicas=IT_temp(T_in_K_old,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_kgs,rho_optic_0)    
    if T_out_K>=T_max_storage:
        outlet=IAPWS97(P=P_op_Mpa, T=T_out_K) 
        if outlet.x>0: #Steam
            outlet=IAPWS97(P=P_op_Mpa, x=0)
            h_out_kJkg=outlet.h
    
            
        else:
            h_out_kJkg=outlet.h
    else:
        outlet=IAPWS97(P=P_op_Mpa, T=T_out_K)
        h_out_kJkg=outlet.h
              
        

    Q_prod=flow_rate_kgs*(h_out_kJkg-h_in_kJkg)*num_loops*FS
    T_out_K=T_max_storage    
    
    return [T_out_K,Perd_termicas,Q_prod,T_in_K_old,flow_rate_kgs]

def operationWaterSimple(bypass,T_in_flag,T_in_K_old,T_in_C_AR,T_out_K_old,T_in_C,P_op_Mpa,bypass_old,T_out_C,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0,num_loops,FS,coef_flow_rec,m_dot_min_kgs,Q_prod_rec_old):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
    [h_in_kJkg,T_in_K]=inputsWithDNIWaterSimple(T_in_flag,T_in_K_old,T_in_C_AR,T_out_K_old,T_in_C,P_op_Mpa,bypass_old)
  
#    gainSolar=DNI*Area*IAM*rho_optic_0
    T_out_K=T_out_C+273 #Target temp
    #Calculo el flowrate necesario para poder dar el salto de temp necesario
    flow_rate_kgs,Perd_termicas=flow_calc (T_out_K,T_in_K,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0)

    if flow_rate_kgs<=m_dot_min_kgs and T_out_K>T_in_K: #El caudal necesario para obtener la temp de salida es inferior al mínimo
        #RECIRCULACION
        flow_rate_rec=coef_flow_rec*m_dot_min_kgs
        T_out_K,Perd_termicas=IT_temp(T_in_K,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_rec,rho_optic_0)    
        Q_prod=0 #No hay produccion
        outlet=IAPWS97(P=P_op_Mpa, T=T_out_K)
        h_out_kJkg=outlet.h
        Q_prod_rec=flow_rate_rec*(h_out_kJkg-h_in_kJkg)
        bypass.append("REC")
        newBypass="REC"
    else:
        #PRODUCCION
        outlet=IAPWS97(P=P_op_Mpa, T=T_out_K)
        h_out_kJkg=outlet.h
        if bypass_old=="REC":
            if Q_prod_rec_old>0:
                Q_prod=flow_rate_kgs*(h_out_kJkg-h_in_kJkg)*num_loops*FS+Q_prod_rec_old*FS #In kW
            else:
                Q_prod=flow_rate_kgs*(h_out_kJkg-h_in_kJkg)*num_loops*FS
        else:
            Q_prod=flow_rate_kgs*(h_out_kJkg-h_in_kJkg)*num_loops*FS #In kW
        flow_rate_rec=0
        Q_prod_rec=0
        bypass.append("PROD")
        newBypass="PROD"
    return [T_out_K,flow_rate_kgs,Perd_termicas,Q_prod,T_in_K,flow_rate_rec,Q_prod_rec,newBypass]

def operationOilSimple(bypass,T_in_K_old,T_out_K_old,T_in_C,P_op_Mpa,bypass_old,T_out_C,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0,num_loops,FS,coef_flow_rec,m_dot_min_kgs,Q_prod_rec_old):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52    
    [T_in_K]=inputsWithDNIOilSimple(T_in_K_old,T_out_K_old,T_in_C,bypass_old)    
    #Calculo el flowrate necesario para poder dar el salto de temp necesario
    T_out_K=T_out_C+273
    T_av_K=(T_in_K+T_out_K)/2
    [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
    
    flow_rate_kgs=1 #kg/s
    T_out_K,Perd_termicas=IT_tempOil(T_in_K,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_kgs,rho_optic_0)

    if flow_rate_kgs<=m_dot_min_kgs and T_out_K>T_in_K: #El caudal necesario para obtener la temp de salida es inferior al mínimo
        #RECIRCULACION
        flow_rate_rec=flow_rate_kgs
        T_out_K,Perd_termicas=IT_tempOil(T_in_K,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_rec,rho_optic_0)    
        Q_prod=0 #No hay produccion
        
        T_av_K=(T_in_K+T_out_K)/2
        [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
        
        Q_prod_rec=flow_rate_rec*Cp_av*(T_out_K-T_in_K)
        bypass.append("REC")
        newBypass="REC"
    else:
        #PRODUCCION
        if bypass_old=="REC":
            if Q_prod_rec_old>0:
                Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS+Q_prod_rec_old*FS #In kWh
            else:
                Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS#In kWh
        else:
            Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS #In kW
        flow_rate_rec=0
        Q_prod_rec=0
        bypass.append("PROD")
        newBypass="PROD"
    return [T_out_K,flow_rate_kgs,Perd_termicas,Q_prod,T_in_K,flow_rate_rec,Q_prod_rec,newBypass]
 

def outputKettle(P_op_Mpa,almVolumen,T_alm_K_old,Q_prod,T_in_C_AR):
    
    almacenamiento=IAPWS97(P=P_op_Mpa, T=T_alm_K_old) #Propiedades en el almacenamiento

    almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
    almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg 
    
    h_sat_vap=IAPWS97(P=P_op_Mpa, x=1).h
    h_sat_liq=IAPWS97(P=P_op_Mpa, x=0).h
    if T_alm_K_old>=IAPWS97(P=P_op_Mpa, x=1).T: #Only Boiling
        m_vap=(Q_prod*3600)/(h_sat_vap-h_sat_liq) #kg
        T_alm=IAPWS97(P=P_op_Mpa, x=1).T
    else:
        Q_to_sat=(almVolumen/(1000*almacenamiento_rho))*(h_sat_liq-IAPWS97(P=P_op_Mpa, T=T_alm_K_old).h)/3600 #In kWh
        if Q_prod>=Q_to_sat: #Heating + Boiling
           Q_for_boiling=Q_prod-Q_to_sat #In kWh
           m_vap=(Q_for_boiling*3600)/(h_sat_vap-h_sat_liq) #kg
           T_alm=IAPWS97(P=P_op_Mpa, x=1).T
        else: #Only Heating
           m_vap=0 #No steam prod 
           h_out=IAPWS97(P=P_op_Mpa, T=T_alm_K_old).h+Q_prod*3600/(almVolumen/(1000*almacenamiento_rho))
           T_alm=IAPWS97(P=P_op_Mpa, h=h_out).T
    
    #Feedwater
    if m_vap!=0:
        h_out_alm=((almVolumen-m_vap)*IAPWS97(P=P_op_Mpa, x=0).h +(m_vap)*IAPWS97(P=P_op_Mpa, T=T_in_C_AR+273).h)/(almVolumen)
        T_alm=IAPWS97(P=P_op_Mpa, h=h_out_alm).T
    else:
        pass
    
    
    return (m_vap/3600, T_alm)




#    newEnerg=(storage_energy_old+Q_prod)*3600 #KJ 
#    almacenamiento=IAPWS97(P=P_op_Mpa, T=T_alm_K_old) #Propiedades en el almacenamiento
#    almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
#    almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg     
#    T_alm_new=(newEnerg/(almacenamiento_CP*almVolumen*(1/1000)*(1/almacenamiento_rho))) #in K

    
def outputOnlyStorageWaterSimple(P_op_Mpa,T_min_storage,T_max_storage,almVolumen,T_in_alm_K,T_alm_K_old,Q_prod,energyStored,Demand,energStorageMax,storage_energy_old,storage_ini_energy): 
    
#    almacenamiento=IAPWS97(P=P_op_Mpa, T=T_alm_K_old) #Propiedades en el almacenamiento
#    almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
#    almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg
#    newEnerg=(storage_energ_old+Q_prod-Demand)*3600 #KJ
    
    if T_min_storage>=T_alm_K_old:
        Q_useful=Q_prod
        energyStored=energyStored+(Q_prod) #New state of the storage
        Q_charg=(Q_prod)
        Q_discharg=0
        
        Q_defoscus=0
        Q_prod_lim=0
        newEnerg=(storage_energy_old+Q_prod)*3600 #KJ   
        almacenamiento=IAPWS97(P=P_op_Mpa, T=T_alm_K_old) #Propiedades en el almacenamiento
        almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
        almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg     
        T_alm_new=(newEnerg/(almacenamiento_CP*almVolumen*(1/1000)*(1/almacenamiento_rho))) #in K
#        SOC=100*(T_alm_new-273)/(T_max_storage-273)
        SOC=100*energyStored/energStorageMax
    
    else:
    
        if Q_prod+energyStored<Demand: #Complete discharge
            Q_prod_lim=Q_prod+energyStored
            Q_useful=Q_prod+energyStored
            Q_discharg=energyStored
            Q_charg=0
            energyStored=0 #New state of the storage
            SOC=0
            Q_defoscus=0
            almacenamiento=IAPWS97(P=P_op_Mpa, T=T_alm_K_old) #Propiedades en el almacenamiento
            almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
            almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg
            newEnerg=storage_ini_energy*3600
            T_alm_new=(newEnerg/(almacenamiento_CP*almVolumen*(1/1000)*(1/almacenamiento_rho))) #in K
           
            
        if (Q_prod<Demand) and (Q_prod+energyStored>Demand): #Partial discharge
            
            energyStored=energyStored-(Demand-Q_prod)#New state of the storage
            Q_charg=0
            Q_discharg=(Demand-Q_prod)
            Q_prod_lim=Demand
            Q_useful=Demand
            Q_defoscus=0
            newEnerg=(storage_energy_old+Q_prod-Demand)*3600 #KJ   
            almacenamiento=IAPWS97(P=P_op_Mpa, T=T_alm_K_old) #Propiedades en el almacenamiento
            almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
            almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg     
            T_alm_new=(newEnerg/(almacenamiento_CP*almVolumen*(1/1000)*(1/almacenamiento_rho))) #in K
            if T_alm_new<=274:
                T_alm_new=274
#            SOC=100*(T_alm_new-273)/(T_max_storage-273)
            SOC=100*energyStored/energStorageMax
    
              
        if (Q_prod>=Demand): #Charging
            if ((Q_prod-Demand)+energyStored)<energStorageMax: #Still room in the storage
                Q_useful=Q_prod
                energyStored=energyStored+(Q_prod-Demand) #New state of the storage
                Q_charg=(Q_prod-Demand)
                Q_discharg=0
                Q_defoscus=0
                Q_prod_lim=Q_prod-Q_charg
                newEnerg=(storage_energy_old+Q_prod-Demand)*3600 #KJ   
                almacenamiento=IAPWS97(P=P_op_Mpa, T=T_alm_K_old) #Propiedades en el almacenamiento
                almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
                almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg     
                T_alm_new=(newEnerg/(almacenamiento_CP*almVolumen*(1/1000)*(1/almacenamiento_rho))) #in K
#                SOC=100*(T_alm_new-273)/(T_max_storage-273)
                SOC=100*energyStored/energStorageMax
            else: #No more room in the storage
                Q_charg=energStorageMax-energyStored
                Q_useful=Demand+(energStorageMax-energyStored)
                Q_discharg=0
                Q_defoscus=Q_prod-Demand-Q_charg
                Q_prod_lim=Q_prod-Q_charg-Q_defoscus
                energyStored=energStorageMax #New state of the storage
                SOC=100
                almacenamiento=IAPWS97(P=P_op_Mpa, T=T_alm_K_old) #Propiedades en el almacenamiento
                almacenamiento_CP=almacenamiento.cp #Capacidad calorifica del proceso KJ/kg/K
                almacenamiento_rho=almacenamiento.v #volumen específico del agua consumida en m3/kg            
                T_alm_new=T_max_storage
                newEnerg=(almVolumen*(1/1000)*(1/almacenamiento_rho)*almacenamiento_CP*(T_max_storage)) #Storage capacity in kWh
            
    newEnerg=newEnerg/3600
    return [T_alm_new,newEnerg,Q_prod_lim,Q_prod,Q_discharg,Q_charg,energyStored,SOC,Q_defoscus,Q_useful]
    
def outputStorageWaterSimple(Q_prod,energyStored,Demand,energStorageMax):
#SL_L_P Supply level with liquid heat transfer media Parallel integration with storage pg52 
    if Q_prod+energyStored<Demand: #Complete discharge
        Q_prod_lim=Q_prod+energyStored
        Q_useful=Q_prod+energyStored
        Q_discharg=energyStored
        Q_charg=0
        energyStored=0 #New state of the storage
        SOC=0
        Q_defoscus=0
       
        
    if (Q_prod<Demand) and (Q_prod+energyStored>Demand): #Partial discharge
        
        energyStored=energyStored-(Demand-Q_prod)#New state of the storage
        Q_charg=0
        Q_discharg=(Demand-Q_prod)
        Q_prod_lim=Demand
        Q_useful=Demand
        SOC=100*energyStored/energStorageMax
        Q_defoscus=0
            
    if (Q_prod>=Demand): #Charging
        if ((Q_prod-Demand)+energyStored)<energStorageMax: #Still room in the storage
            Q_useful=Q_prod
            energyStored=energyStored+(Q_prod-Demand) #New state of the storage
            Q_charg=(Q_prod-Demand)
            Q_discharg=0
            SOC=100*energyStored/energStorageMax
            Q_defoscus=0
            Q_prod_lim=Q_prod-Q_charg
        else: #No more room in the storage
           Q_charg=energStorageMax-energyStored
           Q_useful=Demand+(energStorageMax-energyStored)
           Q_discharg=0
           Q_defoscus=Q_prod-Demand-Q_charg
           Q_prod_lim=Q_prod-Q_charg-Q_defoscus
           energyStored=energStorageMax #New state of the storage
           SOC=100*energyStored/energStorageMax
           
    return [Q_prod_lim,Q_prod,Q_discharg,Q_charg,energyStored,SOC,Q_defoscus,Q_useful]
def outputWithoutStorageWaterSimple(Q_prod,Demand):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
    if Q_prod<=Demand:
        Q_prod_lim=Q_prod
        Q_useful=Q_prod
        Q_defocus=0
    else:
        Q_prod_lim=Demand
        Q_useful=Demand
        Q_defocus=Q_prod-Demand
    return[Q_prod_lim,Q_defocus,Q_useful]

def outputWithoutStorageOilSimple(Q_prod,Demand):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
    if Q_prod<=Demand:
        Q_prod_lim=Q_prod
        Q_useful=Q_prod
        Q_defocus=0
    else:
        Q_prod_lim=Demand
        Q_useful=Demand
        Q_defocus=Q_prod-Demand
    return[Q_prod_lim,Q_defocus,Q_useful]

def outputStorageOilSimple(Q_prod,energyStored,Demand,energStorageMax):
#SL_L_P Supply level with liquid heat transfer media Parallel integration with storage pg52 
    if Q_prod+energyStored<Demand: #Complete discharge
        Q_prod_lim=Q_prod+energyStored
        Q_useful=Q_prod+energyStored
        Q_discharg=energyStored
        Q_charg=0
        energyStored=0 #New state of the storage
        SOC=0
        Q_defoscus=0
       
        
    if (Q_prod<Demand) and (Q_prod+energyStored>Demand): #Partial discharge
        
        energyStored=energyStored-(Demand-Q_prod)#New state of the storage
        Q_charg=0
        Q_discharg=(Demand-Q_prod)
        Q_prod_lim=Demand
        Q_useful=Demand
        SOC=100*energyStored/energStorageMax
        Q_defoscus=0
            
    if (Q_prod>=Demand): #Charging
        if ((Q_prod-Demand)+energyStored)<energStorageMax: #Still room in the storage
            Q_useful=Q_prod
            energyStored=energyStored+(Q_prod-Demand) #New state of the storage
            Q_charg=(Q_prod-Demand)
            Q_discharg=0
            SOC=100*energyStored/energStorageMax
            Q_defoscus=0
            Q_prod_lim=Q_prod-Q_charg
        else: #No more room in the storage
           Q_charg=energStorageMax-energyStored
           Q_useful=Demand+(energStorageMax-energyStored)
           Q_discharg=0
           Q_defoscus=Q_prod-Demand-Q_charg
           Q_prod_lim=Q_prod-Q_charg-Q_defoscus
           energyStored=energStorageMax #New state of the storage
           SOC=100*energyStored/energStorageMax
           
    return [Q_prod_lim,Q_prod,Q_discharg,Q_charg,energyStored,SOC,Q_defoscus,Q_useful]

def moduleSimple(P_0,h_0,QModule,x_0,d_int,Long,m_dot,granoEpsilon):
    if x_0==0 or x_0==1:
        state_0=IAPWS97(P=bar_MPa(P_0), h=h_0)
        P_1=PDCSensible(d_int,P_0,Long,m_dot,granoEpsilon,state_0)   #bar
    else:
        P_1=PDCLatent(d_int,P_0,x_0,Long,m_dot,granoEpsilon)
    h_1=h_0+QModule
    state_1=IAPWS97(P=bar_MPa(P_1), h=h_1)
    T_1=K_C(state_1.T)
    s_1=state_1.s
    x_1=state_1.x
    return [P_1,h_1,T_1,s_1,x_1]

def interconexSimple(P_0,h_0,T_0,s_0,x_0):
    P_1=P_0 #bar
    T_1=T_0 #C
    h_1=h_0 #kJ/kg
    s_1=s_0 #KJ/kgK
    x_1=x_0
    return [P_1,h_1,T_1,s_1,x_1]
    
def PDCSensible(d_int,P_in,Long,m_dot,granoEpsilon,state):
    P_in=bar_MPa(P_in)
    areaInt=np.pi*d_int**2/4
    density=1/state.v
    viscosity=state.mu #Dinamic viscosity Pa*s <-> kg/m*s
    v=m_dot/(density*areaInt) #m/s
    Re=v*d_int*density/viscosity #Reynolds number
    RR=granoEpsilon/d_int
    B=(37530/Re)**16
    A=(2.457*np.log(((7/Re)**0.9+0.27*RR)**(-1)))**16
    f=2*((8/Re)**12+(A+B)**(-1.5))**(1/12)
    deltaP=2*f*density*(v**2)*(Long/d_int)*0.000001
    P_out=P_in-deltaP
    return MPa_bar(P_out)

def PDCLatent(d_int,P_in,x_in,Long,m_dot,granoEpsilon):
    #Using Friedel formula since was the most appropiate at Eck, M., y Steinmann, W.-D., 2005, “Modelling and Design of Direct Solar Steam Generating Collector Fields“, Journal of Solar Energy Engineering, 127 (3), pp. 371-380.
    P_in=bar_MPa(P_in)
    RR=granoEpsilon/d_int
    areaInt=np.pi*d_int**2/4
    #Liquid phaseS_FWS
    state_liq=IAPWS97(P=P_in, x=0)
    density_liq=1/state_liq.v
    viscosity_liq=state_liq.mu #Dinamic viscosity Pa*s <-> kg/m*s
    v_liq=m_dot/(density_liq*areaInt) #m/s
    Re_liq=v_liq*d_int*density_liq/viscosity_liq #Reynolds number
    B=(37530/Re_liq)**16
    A=(2.457*np.log(((7/Re_liq)**0.9+0.27*RR)**(-1)))**16
    f_liq=2*((8/Re_liq)**12+(A+B)**(-1.5))**(1/12)
    
    #Steam phase
    state_steam=IAPWS97(P=P_in, x=1)
    density_steam=1/state_steam.v
    viscosity_steam=state_steam.mu #Dinamic viscosity Pa*s <-> kg/m*s
    v_steam=m_dot/(density_steam*areaInt) #m/s
    Re_steam=v_steam*d_int*density_steam/viscosity_steam #Reynolds number
    B=(37530/Re_steam)**16
    A=(2.457*np.log(((7/Re_steam)**0.9+0.27*RR)**(-1)))**16
    f_steam=2*((8/Re_steam)**12+(A+B)**(-1.5))**(1/12)
    
    A=(1-x_in)**2+(x_in**2)*((density_liq*f_liq)/(density_steam*f_steam))
    Fr_liq=(16*m_dot**2)/(np.pi**2*density_liq**2*9.81*d_int**5)
    sigma=state_steam.sigma #Surface tension N/m
    We_liq=(16*m_dot**2)/(np.pi**2*d_int**3*sigma*density_liq)
    
    #Friedel formula
    R=A+3.43*x_in**0.685*(1-x_in)**.24*(density_liq/density_steam)**.8*(viscosity_steam/viscosity_liq)**.22*(1-(viscosity_steam/viscosity_liq))**.89*Fr_liq**(-.047)*We_liq**(-0.0334)
    
    deltaP_liq=2*f_liq*density_liq*v_liq**2*(Long/d_int)*(0.000001) #MPa conversion from MPa/kg/ms2
    deltaP_steam=2*f_steam*density_steam*v_steam**2*(Long/d_int)*(0.000001) #MPa conversion from MPa/kg/ms2
    deltaP=R*deltaP_liq
    if deltaP>deltaP_steam:
        deltaP=deltaP_steam
    else:
        deltaP=deltaP
    P_out=P_in-deltaP
    return MPa_bar(P_out)
