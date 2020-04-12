# -*- coding: utf-8 -*-
"""
Integration schemes from task 49
Created on Sat May  5 20:06:05 2018

version: 1.0



@author: miguel frasquet (SOLATOM)
"""

from iapws import IAPWS97
import numpy as np
from Solar_modules.iteration_process import flow_calc, flow_calcHTF
from Solar_modules.iteration_process import IT_temp
from General_modules.func_General import thermalOil,moltenSalt
from General_modules.func_General import bar_MPa,MPa_bar,K_C
from Collector_modules.receivers import Rec_loss

def offSimple(fluidInput,bypass,T_in_flag,T_in_C_AR,temp):
            
    bypass.append("OFF")
    
    if fluidInput=="water":
        if T_in_flag==1: # Closed circuit
            T_in_K=temp
        else:
            T_in_K=T_in_C_AR+273 # Input from public water grid
    if fluidInput=="oil" or fluidInput=="moltenSalt" or fluidInput=="steam":
        T_in_K=temp
    T_out_K=temp
    Q_prod=0 # There's no production  
    return [T_out_K,Q_prod,T_in_K]

def offDSG_Rec(PerdSD,SD_limit_energy,fluidInput,bypass,T_in_flag,T_in_C_AR,temp,SD_energy_old,SD_mass,T_SD_K_old,P_op_Mpa):
            
    bypass.append("OFF")
     
    T_in_K=T_out_K=temp
    Q_prod=0 # There's no production 
    
    #Simplified ambient losses
    SD_energy=SD_energy_old-PerdSD  
    try:
        SDState=IAPWS97(P=P_op_Mpa, T=T_SD_K_old)
    except:        
        raise ValueError('Error in steam drum',T_SD_K_old-273)

    SD_h=3600*SD_energy/SD_mass
    SDState=IAPWS97(P=P_op_Mpa, h=SD_h)
    T_SD_K=SDState.T
        
    if T_SD_K<283 or SD_energy<SD_limit_energy: #Avoid cooling more than ambient temp or limit
        T_SD_K=283
        SD_energy=SD_energy_old
    
    return [T_out_K,Q_prod,T_in_K,T_SD_K,SD_energy]

#def offOilSimple(bypass,T_in_K_old):
#         
#    bypass.append("OFF")
#    T_in_K=T_in_K_old
#    T_out_K=0+273
#    Q_prod=0 # There's no production   
#    return [T_out_K,Q_prod,T_in_K]

#def offSteamSimple(bypass,T_in_K_old):
#         
#    bypass.append("OFF")
#    T_in_K=T_in_K_old
#    T_out_K=temp
#    Q_prod=0 # There's no production   
#    return [T_out_K,Q_prod,T_in_K]

def offStorageSimple(fluidInput,bypass,T_in_flag,T_in_C_AR,temp,energStorageMax,energy_stored):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52             
    bypass.append("OFF")
    if fluidInput=="water":
        if T_in_flag==1:
            T_in_K=temp
        else:
            T_in_K=T_in_C_AR+273
    if fluidInput=="oil" or fluidInput=="moltenSalt" or fluidInput=="steam":
        T_in_K=temp      
    T_out_K=temp
    Q_prod=0 #No hay produccion
    SOC=100*energy_stored/energStorageMax
    return [bypass,T_out_K,Q_prod,T_in_K,SOC]
def offOnlyStorageSimple(temp,energStorageMax,energy_stored,T_K_alm_old,storage_energy_old,SOC_old):

    T_in_K=temp

    T_out_K=temp
    Q_prod=0 #No hay produccion
#    SOC=100*(T_K_alm_old-273)/(T_max_storage-273)
#    SOC=100*energy_stored/energStorageMax
    SOC=SOC_old
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

def inputsWithDNI_HTFSimple(T_in_K_old,T_out_K_old,T_in_C,bypass_old):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 

    if bypass_old=="REC" and T_out_K_old>(T_in_C+273):
        T_in_K=T_out_K_old
    else:
        T_in_K=T_in_C+273

    return [T_in_K]
def operationOilKettleSimple(bypass,T_in_K_old,T_out_K_old,T_in_C,P_op_Mpa,bypass_old,T_out_C,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0,num_loops,FS,coef_flow_rec,m_dot_min_kgs,Q_prod_rec_old,T_alm_K,DeltaKettle):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52    
    [T_in_K]=inputsWithDNI_HTFSimple(T_in_K_old,T_out_K_old,T_in_C,bypass_old)    
    #Calculo el flowrate necesario para poder dar el salto de temp necesario
    fluidInput="oil"
    T_out_K=T_out_C+273
    T_av_K=(T_in_K+T_out_K)/2
    [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
    
    flow_rate_kgs=1 #kg/s
    T_out_K,Perd_termicas=IT_temp(fluidInput,T_in_K,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_kgs,rho_optic_0)

    if T_out_K<T_alm_K+DeltaKettle:
        #RECIRCULACION
        flow_rate_rec=flow_rate_kgs
        T_out_K,Perd_termicas=IT_temp(fluidInput,T_in_K,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_rec,rho_optic_0)    
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
                Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS+Q_prod_rec_old*num_loops*FS #In kWh
            else:
                Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS#In kWh
        else:
            Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS #In kW
        flow_rate_rec=0
        Q_prod_rec=0
        bypass.append("PROD")
        newBypass="PROD"
    return [T_out_K,flow_rate_kgs,Perd_termicas,Q_prod,T_in_K,flow_rate_rec,Q_prod_rec,newBypass]
    
def operationOnlyStorageSimple(fluidInput,T_max_storage,T_in_K_old,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0,num_loops,FS,flow_rate_kgs,type_coll,sender):
#SL_L_S Supply level with liquid heat transfer media just for heat a storage
    
    if sender == 'CIMAV':
        from CIMAV.CIMAV_modules.iteration_process import IT_temp_CIMAV
        T_out_K,Perd_termicas=IT_temp_CIMAV(fluidInput,T_in_K_old,T_max_storage,P_op_Mpa,temp,DNI,IAM,Area,n_coll_loop,flow_rate_kgs,Area_coll,rho_optic_0_coll,eta1_coll,eta2_coll,mdot_test_permeter_coll)
    else:
        T_out_K,Perd_termicas=IT_temp(fluidInput,T_in_K_old,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_kgs,rho_optic_0)
    
    if fluidInput =="water":
        inlet=IAPWS97(P=P_op_Mpa, T=T_in_K_old)
        h_in_kJkg=inlet.h
    
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
        
    elif fluidInput =="oil":
        [SF_inlet_rho,SF_inlet_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_in_K_old)
        [SF_outlet_rho,SF_outlet_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_out_K)
        SF_avg_Cp=(SF_outlet_Cp+SF_inlet_Cp)/2
        Q_prod=flow_rate_kgs*SF_avg_Cp*(T_out_K-T_in_K_old)*num_loops*FS #kWh
        
    elif fluidInput =="moltenSalt":
        [rho,SF_inlet_Cp,k,Dv]=moltenSalt(T_in_K_old)
        [rho,SF_outlet_Cp,k,Dv]=moltenSalt(T_out_K)
        SF_avg_Cp=(SF_outlet_Cp+SF_inlet_Cp)/2
        Q_prod=flow_rate_kgs*SF_avg_Cp*(T_out_K-T_in_K_old)*num_loops*FS #kWh
        
        
    #T_out_K=T_max_storage    #Not used
    
    return [T_out_K,Perd_termicas,Q_prod,T_in_K_old,flow_rate_kgs]


def operationSimple(fluidInput,bypass,T_in_flag,T_in_K_old,T_in_C_AR,T_out_K_old,T_in_C,P_op_Mpa,bypass_old,T_out_C,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0,num_loops,FS,coef_flow_rec,m_dot_min_kgs,Q_prod_rec_old, sender,Area_coll,rho_optic_0_coll,eta1_coll,eta2_coll,mdot_test_permeter_coll):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
    if fluidInput=="water" or fluidInput=="steam":
        [h_in_kJkg,T_in_K]=inputsWithDNIWaterSimple(T_in_flag,T_in_K_old,T_in_C_AR,T_out_K_old,T_in_C,P_op_Mpa,bypass_old)
    elif fluidInput=="oil":
        [T_in_K]=inputsWithDNI_HTFSimple(T_in_K_old,T_out_K_old,T_in_C,bypass_old)
    elif fluidInput=="moltenSalt":
        [T_in_K]=inputsWithDNI_HTFSimple(T_in_K_old,T_out_K_old,T_in_C,bypass_old)  
    
    T_out_K=T_out_C+273 #Target temp
    
    if sender == 'CIMAV':
        from CIMAV.CIMAV_modules.iteration_process import flow_calc_CIMAV,IT_temp_CIMAV
        flow_rate_kgs,Perd_termicas = flow_calc_CIMAV(fluidInput,T_out_K,T_in_K,P_op_Mpa,temp,DNI,IAM,Area,Area_coll,rho_optic_0_coll,eta1_coll,eta2_coll,mdot_test_permeter_coll) #Works for moltensalts,water,thermaloil
        
    else:
        if fluidInput=="water" or fluidInput=="steam":
            #Calculo el flowrate necesario para poder dar el salto de temp necesario
            flow_rate_kgs,Perd_termicas=flow_calc(T_out_K,T_in_K,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0)
        
        elif fluidInput=="oil":
            T_av_K=(T_in_K+T_out_K)/2
            [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
            [flow_rate_kgs,Perd_termicas]=flow_calcHTF(T_out_K,T_in_K,Cp_av,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0)
        
        elif fluidInput=="moltenSalt":
            T_av_K=(T_in_K+T_out_K)/2
            [rho_av,Cp_av,k_av,Dv_av]=moltenSalt(T_av_K)
            [flow_rate_kgs,Perd_termicas]=flow_calcHTF (T_out_K,T_in_K,Cp_av,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0)

    

    if flow_rate_kgs<=m_dot_min_kgs and T_out_K>T_in_K: #El caudal necesario para obtener la temp de salida es inferior al mínimo
        #RECIRCULACION
        flow_rate_rec=coef_flow_rec*m_dot_min_kgs
        if sender == 'CIMAV':
            T_out_K,Perd_termicas = IT_temp_CIMAV(fluidInput,T_in_K,T_out_K,P_op_Mpa,temp,DNI,IAM,Area,n_coll_loop,flow_rate_rec,Area_coll,rho_optic_0_coll,eta1_coll,eta2_coll,mdot_test_permeter_coll)
        else:
            T_out_K,Perd_termicas = IT_temp(fluidInput,T_in_K,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_rec,rho_optic_0)    
        Q_prod=0 #No production
        
        if fluidInput=="water" or fluidInput=="steam":
            outlet=IAPWS97(P=P_op_Mpa, T=T_out_K)
            h_out_kJkg=outlet.h
            Q_prod_rec=flow_rate_rec*(h_out_kJkg-h_in_kJkg)
        
        elif fluidInput=="oil":
            T_av_K=(T_in_K+T_out_K)/2
            [rho_av,Cp_av,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
            Q_prod_rec=flow_rate_rec*Cp_av*(T_out_K-T_in_K)
        
        elif fluidInput=="moltenSalt":
            T_av_K=(T_in_K+T_out_K)/2
            [rho_av,Cp_av,k_av,Dv_av]=moltenSalt(T_av_K)
            Q_prod_rec=flow_rate_rec*Cp_av*(T_out_K-T_in_K)
            
        Q_prod_rec=Q_prod_rec+Q_prod_rec_old      
        bypass.append("REC")
        newBypass="REC"      
        
    else:
        #PRODUCCION
        
        if fluidInput=="water" or fluidInput=="steam":
            outlet=IAPWS97(P=P_op_Mpa, T=T_out_K)
            h_out_kJkg=outlet.h
            if bypass_old=="REC":
                if Q_prod_rec_old>0:
                    Q_prod=flow_rate_kgs*(h_out_kJkg-h_in_kJkg)*num_loops*FS+Q_prod_rec_old*num_loops*FS #In kW
                else:
                    Q_prod=flow_rate_kgs*(h_out_kJkg-h_in_kJkg)*num_loops*FS
            else:
                Q_prod=flow_rate_kgs*(h_out_kJkg-h_in_kJkg)*num_loops*FS #In kW
        
        if fluidInput=="oil":
            if bypass_old=="REC":
                if Q_prod_rec_old>0:
                    Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS+Q_prod_rec_old*num_loops*FS #In kWh
                else:
                    Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS#In kWh
            else:
                Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS #In kW
               
        if fluidInput=="moltenSalt":
            if bypass_old=="REC":
                if Q_prod_rec_old>0:
                    Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS+Q_prod_rec_old*num_loops*FS #In kWh
                else:
                    Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS#In kWh
            else:
                Q_prod=flow_rate_kgs*Cp_av*(T_out_K-T_in_K)*num_loops*FS #In kW
                
        flow_rate_rec=0
        Q_prod_rec=0
        bypass.append("PROD")
        newBypass="PROD"
    return [T_out_K,flow_rate_kgs,Perd_termicas,Q_prod,T_in_K,flow_rate_rec,Q_prod_rec,newBypass]


def operationDSG(bypass,bypass_old,T_out_K_old,T_in_C,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0,num_loops,FS,coef_flow_rec,m_dot_min_kgs,x_desing,Q_prod_rec_old,subcooling):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
    Perd_termicas=0
    T_in_K=T_in_C+273 #Normal operation
    if bypass_old=="REC" and T_out_K_old>(T_in_C+273):
        T_in_K=T_out_K_old

        
    outlet=IAPWS97(P=P_op_Mpa, x=x_desing) #Design conditions
    inlet=IAPWS97(P=P_op_Mpa, T=T_in_K)
    h_in_kJkg=inlet.h
    
    DELTA_T_loss=outlet.T-temp
    Q_loss_rec=Rec_loss(REC_type,DELTA_T_loss,theta_i_rad,DNI) #W/m
    # Q_loss_rec=Q_loss_rec[0]/(n_coll_loop*Long*n_loops)
    Q_loss_rec=Q_loss_rec[0]
    flow_rate_kgs=(DNI*IAM*Area*rho_optic_0-Q_loss_rec*n_coll_loop*Long)/((outlet.h-inlet.h)*1000)

    if flow_rate_kgs<=m_dot_min_kgs: #Recirculación
        flow_rate_rec=m_dot_min_kgs*coef_flow_rec #New flow_rate
        #New enthalpy at the output  
        h_out_kJkg=(((DNI*IAM*Area*rho_optic_0-Q_loss_rec*n_coll_loop*Long)/flow_rate_rec)/1000)+inlet.h
        if h_out_kJkg<=h_in_kJkg: #The recirculation generates losses
            h_out_kJkg=h_in_kJkg
            x_out=IAPWS97(P=P_op_Mpa, h=h_out_kJkg).x
            Q_prod=0
            Q_prod_rec=0
            T_out_K=T_in_K
            flow_rate_kgs=0
        else:
            x_out=IAPWS97(P=P_op_Mpa, h=h_out_kJkg).x
            if x_out<=0: #After the recirculation the fluid still liquid
                Q_prod=0
                # Q_prod_rec=(DNI*IAM*Area*rho_optic_0-Q_loss_rec*n_coll_loop*Long)*num_loops*FS/1000
                T_out_K,Perd_termicas=IT_temp("steam",T_in_K,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_rec,rho_optic_0)    
                Perd_termicas=Perd_termicas/1000
                outlet=IAPWS97(P=P_op_Mpa, T=T_out_K)
                h_out_kJkg=outlet.h
                Q_prod_rec=flow_rate_rec*(h_out_kJkg-h_in_kJkg)*num_loops*FS
                
            else: #After the recirculation the fluid is biphasic and this could generate problems with the pump
                T_sub=IAPWS97(P=P_op_Mpa, x=0).T-subcooling
                h_sub=IAPWS97(P=P_op_Mpa, T=T_sub).h
                Q_prod_rec=(DNI*IAM*Area*rho_optic_0-Q_loss_rec*n_coll_loop*Long)*FS/1000 #Q_prod_rec to calculate flow_rate inside the loop
                #Try-Except in order to avoid infinite flow rate when h_out=h_in (after several unsuccessful attempts to reach x_out)
                if h_sub-h_in_kJkg>0:
                    flow_rate_rec=Q_prod_rec/(h_sub-h_in_kJkg)
                else:
                    flow_rate_rec=0
                    
                Q_prod=0
                T_out_K=outlet.T
                Q_prod_rec=Q_prod_rec*num_loops*FS # Total Q_prod_rec in the field
        Q_prod_rec=Q_prod_rec+Q_prod_rec_old   
        bypass.append("REC")
        newBypass="REC" 
    else:    
        if bypass_old=="REC":
            if Q_prod_rec_old>0:
                Q_prod=flow_rate_kgs*(outlet.h-h_in_kJkg)*num_loops*FS+Q_prod_rec_old #In kW
            else:
                Q_prod=flow_rate_kgs*(h_out_kJkg-h_in_kJkg)*num_loops*FS
        else:
            x_out=x_desing
            outlet=IAPWS97(P=P_op_Mpa, x=x_out)
            Q_prod=flow_rate_kgs*(outlet.h-h_in_kJkg)*num_loops*FS #In kW
                
        x_out=x_desing
        T_out_K=IAPWS97(P=P_op_Mpa, x=x_out).T
        Q_prod_rec=0
        flow_rate_rec=0
        bypass.append("PROD")
        newBypass="PROD" 
    if Perd_termicas==0:
        Perd_termicas=Q_loss_rec*n_coll_loop*Long/1000

    return [flow_rate_kgs,Perd_termicas,Q_prod,T_in_K,x_out,T_out_K,flow_rate_rec,Q_prod_rec,bypass]


def operationDSG_Rec(m_dot_min_kgs,bypass,SD_min_energy,T_SD_K_old,SD_mass,SD_energy_old,T_in_C,P_op_Mpa,temp,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0,num_loops,FS,x_desing,PerdSD):
#SL_L_P Supply level with liquid heat transfer media Parallel integration pg52 
    Perd_termicas=0
    
    #Solar Loop
    #Inlet
    T_in_K=T_SD_K_old #The inlet temp. of the solar field is equal to the temperature of the SD (in the prev. step)
    inlet=IAPWS97(P=P_op_Mpa, T=T_in_K)
    h_in_kJkg=inlet.h
    #Outlet
    outlet=IAPWS97(P=P_op_Mpa, x=x_desing)
    h_out_kJkg=outlet.h
    T_out_K=outlet.T
    
    #Flow rate in the solar field calculation
    DELTA_T_loss=outlet.T-temp
    Q_loss_rec=Rec_loss(REC_type,DELTA_T_loss,theta_i_rad,DNI) #W/m
    Q_loss_rec=Q_loss_rec[0]
    flow_rate_kgs=(DNI*IAM*Area*rho_optic_0-Q_loss_rec*n_coll_loop*Long)/((outlet.h-inlet.h)*1000)

    if flow_rate_kgs<=m_dot_min_kgs:
        #Energy coming from Solar field
        flow_rate_kgs=m_dot_min_kgs        
        Q_prod=(DNI*IAM*Area*rho_optic_0-Q_loss_rec*n_coll_loop*Long)/1000
        Q_prod=Q_prod*num_loops*FS
    else:
        #Energy coming from Solar field
        Q_prod=flow_rate_kgs*(h_out_kJkg-h_in_kJkg)*num_loops*FS
    
    #New energy state of the Steam Drum
    SD_energy_new=SD_energy_old+Q_prod-PerdSD
    SD_h=3600*SD_energy_new/SD_mass
    SDState=IAPWS97(P=P_op_Mpa, h=SD_h)
    T_SD_K=SDState.T
    
    #Quantity of steam delivered to the process
    if SD_energy_new>SD_min_energy:
        Q_prod_steam=SD_energy_new-SD_min_energy
        SD_energy_new=SD_min_energy
        T_SD_K=IAPWS97(P=P_op_Mpa, x=0).T
        
    else:
        if IAPWS97(P=P_op_Mpa, T=T_SD_K).x==1:
            T_SD_K=IAPWS97(P=P_op_Mpa, x=0).T 
        Q_prod_steam=0
    
    bypass.append("PROD")
    return [flow_rate_kgs,Perd_termicas,Q_prod,T_in_K,T_out_K,T_SD_K,SD_energy_new,Q_prod_steam]




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


def outputOnlyStorageSimple(fluidInput,P_op_Mpa,T_min_storage,T_max_storage,almVolumen,T_in_alm_K,T_alm_K_old,Q_prod,energy_stored,Demand,energStorageMax,storage_energy_old,storage_ini_energy,storage_min_energy,energStorageUseful,storage_max_energy):    
    if T_min_storage>=T_alm_K_old: # The storage is still under the minimum temperatura -> Charge
        #energy_stored: is the energy above/under the storage_min_energy(energy at the minimum/initial/inlet design temperature) that the previous hour left as result in the storage. This is the available energy from the preious step
        #energStorageUseful: is the energy difference between the energy that the storage would have at the T_max_storage temperature and thes storage_min_energy(energy at the minimum/minimum/initial/inlet)
        #storage_energy_old: is the total energy that the storage had in the previous hour, this includes the energy that corresponds to temperatures lower than the one for the inlet design.
        if ((Q_prod)+energy_stored)<(storage_max_energy-storage_energy_old): # A.1 still room in the storage. Is the total available energy less than the posible available energy? if so all of it is stored.
            Q_useful=Q_prod #All the produced energy is useful and will be charged up in the storage.
            energy_stored=0 #Reset the available energy for the next hour, this will be calculated later in case the temperature has raised enough.
            Q_charg=(Q_prod) #All the produced energy is stored in the storage.
            Q_discharg=0 #No energy is wasted
            Q_defocus=0 #No energy is wasted
            Q_prod_lim=0 #No energy is wasted
            storage_energy_new=(storage_energy_old+Q_prod)*3600 #KJ #The new energy that the storage will have is the previous total energy plus the produced. Nothing is send to the process because the energy is used to heat the storage
            
            #Calculates the properties of the fluid
            if fluidInput=="water":
                storage=IAPWS97(P=P_op_Mpa, T=T_alm_K_old) #Storage properties
                storage_Cp=storage.cp #Specific Heat KJ/kg/K
                storage_rho=storage.rho #Storage density [kg/m2]
            elif fluidInput=="oil":
                [storage_rho,storage_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_alm_K_old)
            elif fluidInput=="moltenSalt":
                [storage_rho,storage_Cp,k,Dv]=moltenSalt(T_alm_K_old)
            
            T_alm_new=(storage_energy_new/(storage_Cp*almVolumen*(1/1000)*(storage_rho))) #in K #The new temperature of the storage with the energy that gained in this hour.
            
            if T_alm_new>T_min_storage: #in case that the new temperature is larger than the minimum temperature of the storage 
                energy_stored=(storage_energy_new/3600-storage_min_energy)  #Calculates the energy above the minimum level of energy
           
            if fluidInput=="water" and IAPWS97(P=P_op_Mpa, T=T_alm_new).x>0: #Steam in the storage danger!! #If the fluid is water, it is possible that the temperature is so high that it became steam
                #This shouldn't happen since in the variable initialization the posible case of steam was handeled by setting the energyStorageMax, but just in case
                T_alm_new=IAPWS97(P=P_op_Mpa, x=0).T #If steam started to form the new temperature of storage is set to the limit at wich the steam starts to form
                #In this case some of the energy is lost
                
            SOC=100*(storage_energy_new/3600-storage_min_energy)/energStorageUseful #Calculates the porcentage of storage used (Juan: I guess)
        
        else: # A.2 No more room for storage #The available energy is more than what the storage could handle. Q_prod > energStorageUseful-energy_stored+Demand
            
            Q_charg=energStorageUseful-energy_stored #The storage is charged to the maximum.
            Q_useful=energStorageUseful-energy_stored #The energy that could be use. This could be obtained from the condition of the "if"
            Q_discharg=0 #The storage temperature is lower than the minimum so no discharge
            Q_defocus=Q_prod-Q_charg #The extra energy that could not be used is the difference between the produced energy and the useful energy
            Q_prod_lim= 0 #The storage temperature is lower than the minimum so no production
            energy_stored=energStorageUseful #New state of the storage #The storage is fully charged and all the posible available enery is available
            SOC=100 #The storage is fully charged
            T_alm_new=T_max_storage  #Since the storage is fully charged its temperature is the maximum temperature
            storage_energy_new=storage_max_energy*3600 #KJ #The storage is fully charged

    
    else: #The previous temperature of the storage is larger than the minimum limit, so there is energy available in the storage.
    
        if Q_prod+energy_stored<=Demand: #B.2 Complete discharge #All the available energy is less than the demand so all has to be used.
            Q_prod_lim=Q_prod+energy_stored #All the available energy is used to feed the process
            Q_useful=Q_prod+energy_stored #All the energy is useful
            Q_discharg=energy_stored #All the energy is discharged
            Q_charg=0 #Nothing has charged, all used for the process
            energy_stored=0 #New state of the storage #Now the storage has no available energy
            SOC=0 #0% of the storage available
            Q_defocus=0 #Nothing is wasted
            storage_energy_new=(storage_energy_old-Q_discharg)*3600 #From the total energy that the storage had in the previous step, now it has Q_discharg less energy (which should be the same as the same as the minimum possible energy that the storage could have in total)
            T_alm_new=T_min_storage+0.0001 #in K #Since now it has the minimum energy posible then it has the minimum temperature posible
            
        elif (Q_prod<Demand) and (Q_prod+energy_stored>Demand): # B.1 Partial discharge
            
            Q_discharg=(Demand-Q_prod) #Extra energy necessary to fullfill the demand
            energy_stored=energy_stored-Q_discharg #(Demand-Q_prod) #New state of the storage #The new available energy is the previous available energy minus the energy necessary to complete the demand 
            Q_charg=0 #No charge
            Q_prod_lim=Demand #The demand has been fullfilled
            Q_useful=Demand #The energy that has been useful is the same as the demand
            Q_defocus=0 #Nothing is wasted
            storage_energy_new=(storage_energy_old+Q_prod-Demand)*3600 #KJ #The new energy available is the total previous energy plus the produced energy minus the demanded energy
            
            #Calculates the fluid temperatures for calculating the new temperature of the storage
            if fluidInput=="water":
                storage=IAPWS97(P=P_op_Mpa, T=T_alm_K_old) #Storage properties
                storage_Cp=storage.cp #Specific Heat KJ/kg/K
                storage_rho=storage.rho #Storage density [kg/m2]
            elif fluidInput=="oil":
                [storage_rho,storage_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_alm_K_old)
            elif fluidInput=="moltenSalt":
                [storage_rho,storage_Cp,k,Dv]=moltenSalt(T_alm_K_old)
            
            T_alm_new=(storage_energy_new/(storage_Cp*almVolumen*(1/1000)*(storage_rho))) #in K #Calculates the new temperature of the storage.
            
            if T_alm_new<=274: #Avoid absolute zero
                T_alm_new=274

            SOC=100*(storage_energy_new/3600-storage_min_energy)/energStorageUseful #Porcentage of the storage tha is occupied.
             
        else: #Charging #In this case the energy produced is larger than the demand,then the the storage charges up
            if ((Q_prod-Demand)+energy_stored)<energStorageUseful and (T_alm_K_old<T_max_storage): # B.3.2 Still room in the storage for the full production
                Q_useful=Q_prod#All the energy is useful since it can be either stored or used
                Q_charg=(Q_prod-Demand) #The extra available energy after covering the demand.
                energy_stored=energy_stored+(Q_charg) #New state of the storage #The extra energy after the demand is covered plus the previous total energy
                Q_discharg=0 #No energy is taken from the storage
                Q_defocus=0 #No energy is wasted
                Q_prod_lim=Demand #Q_prod-Q_charg #This is the demanded energy too.
                storage_energy_new=(storage_energy_old+Q_charg)*3600 #KJ #The new energy of the storage is the previous total energy plus the energy that charged up
                
                #Calculates the fluid temperatures    
                if fluidInput=="water":
                    storage=IAPWS97(P=P_op_Mpa, T=T_alm_K_old) #Storage properties
                    storage_Cp=storage.cp #Specific Heat KJ/kg/K
                    storage_rho=storage.rho #Storage density [kg/m2]
                elif fluidInput=="oil":
                    [storage_rho,storage_Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_alm_K_old)
                elif fluidInput=="moltenSalt":
                    [storage_rho,storage_Cp,k,Dv]=moltenSalt(T_alm_K_old)
            
                T_alm_new=(storage_energy_new/(storage_Cp*almVolumen*(1/1000)*(storage_rho))) #in K #Calculates the new temperature
                
                if fluidInput=="water" and IAPWS97(P=P_op_Mpa, T=T_alm_new).x>0: #Steam in the storage danger!! #In the unlikely case that the new temperature is over the vapor temperatue of water assign a new storage temperature, some energy is lost and should be calculated.
                    T_alm_new=IAPWS97(P=P_op_Mpa, x=0).T

                SOC=100*(storage_energy_new/3600-storage_min_energy)/energStorageUseful #The new porcentage of storage that is occupied
                
            else: # B.3.1 No more room in the storage. #In the case when the produced energy is more than the demand and the one that could be possibly stored
                if (T_alm_K_old<T_max_storage): #In the previous hour the storage temperature was less than the maximum posible storage temperature
                    Q_charg=energStorageUseful-energy_stored #The energy that will be charged up is the one missing to fully chage the storage
                    Q_useful=Demand+Q_charg #(energStorageUseful-energy_stored) #The energy that could be used is the one to cover the deman plus the one to fully charge the storage
                else:#If the previous temperature is larger or the same as the maximum possible temperature
                    Q_charg=0 #Nothing is charged
                    Q_useful=Demand #Only the energy to cover the demand is useful
                    
                Q_discharg=0 #No energy was discharged
                Q_defocus=Q_prod-Q_useful #Demand-Q_charg #Some energy is lost, the lost energy is the difference between what was used (charge up the storage and to cover the demand) and the one produced
                Q_prod_lim=Demand #This is the same as the demand
                energy_stored=energStorageUseful #New state of the storage #Completely full
                SOC=100 #The storage is 100% occupied
                T_alm_new=T_max_storage #The new temperature of the storage is the maxiumum temperature since it is fully cahrged
                storage_energy_new=storage_max_energy*3600 #kJ #The new total energy
            
    storage_energy_new=storage_energy_new/3600 #Changes from kJ -> kWh
    return [T_alm_new,storage_energy_new,Q_prod_lim,Q_prod,Q_discharg,Q_charg,energy_stored,SOC,Q_defocus,Q_useful]
  


def outputStorageSimple(Q_prod,energy_stored,Demand,energStorageMax):
#SL_L_P Supply level with liquid heat transfer media Parallel integration with storage pg52 
    if Q_prod+energy_stored<Demand: #Complete discharge
        Q_prod_lim=Q_prod+energy_stored
        Q_useful=Q_prod+energy_stored
        Q_discharg=energy_stored
        Q_charg=0
        energy_stored=0 #New state of the storage
        SOC=0
        Q_defocus=0
        
    elif (Q_prod<Demand) and (Q_prod+energy_stored>Demand): #Partial discharge
        
        energy_stored=energy_stored-(Demand-Q_prod)#New state of the storage
        Q_charg=0
        Q_discharg=(Demand-Q_prod)
        Q_prod_lim=Demand
        Q_useful=Demand
        SOC=100*energy_stored/energStorageMax
        Q_defocus=0
            
    elif (Q_prod>=Demand): #Charging
        if ((Q_prod-Demand)+energy_stored)<energStorageMax: #Still room in the storage
            Q_useful=Q_prod
            energy_stored=energy_stored+(Q_prod-Demand) #New state of the storage
            Q_charg=(Q_prod-Demand)
            Q_discharg=0
            SOC=100*energy_stored/energStorageMax
            Q_defocus=0
            Q_prod_lim=Q_prod-Q_charg
        else: #No more room in the storage
           Q_charg=energStorageMax-energy_stored
           Q_useful=Demand+(energStorageMax-energy_stored)
           Q_discharg=0
           Q_defocus=Q_prod-Demand-Q_charg
           Q_prod_lim=Q_prod-Q_charg-Q_defocus
           energy_stored=energStorageMax #New state of the storage
           SOC=100*energy_stored/energStorageMax
           
    return [Q_prod_lim,Q_prod,Q_discharg,Q_charg,energy_stored,SOC,Q_defocus,Q_useful]

def outputWithoutStorageSimple(Q_prod,Demand):
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

def outputDSG_Rec(SD_max_energy,SD_min_energy,SD_energy,SD_energy_old,Q_prod,Q_prod_steam,Demand):
#SL_S_PDR
    if Q_prod_steam<=Demand:
        Q_prod_lim=Q_prod_steam
        Q_useful=Q_prod
        Q_drum=max(0,SD_energy-SD_energy_old) #Q_drum cannot be negative
        Q_defocus=0
    else:
        if SD_energy+Q_prod_steam-Demand<SD_max_energy: #All the excess is absorbed by the steam drum
            SD_energy=SD_energy+Q_prod_steam-Demand
            Q_prod_lim=Demand
            Q_useful=Q_prod_steam
            Q_drum=Q_prod_steam-Demand
            Q_defocus=0
            Q_prod_steam=Demand
        else:
            Q_drum=(SD_max_energy-SD_min_energy)
            Q_defocus=Q_prod_steam-Demand-(SD_max_energy-SD_min_energy)
            Q_prod_steam=Demand
            SD_energy=SD_max_energy
            Q_prod_lim=Demand
            Q_useful=Q_drum+Q_prod_steam
            
    return[Q_prod_lim,Q_defocus,Q_useful,SD_energy,Q_prod_steam,Q_drum]

def outputStorageOilSimple(Q_prod,energy_stored,Demand,energStorageMax):
#SL_L_P Supply level with liquid heat transfer media Parallel integration with storage pg52 
    if Q_prod+energy_stored<Demand: #Complete discharge
        Q_prod_lim=Q_prod+energy_stored
        Q_useful=Q_prod+energy_stored
        Q_discharg=energy_stored
        Q_charg=0
        energy_stored=0 #New state of the storage
        SOC=0
        Q_defocus=0
       
        
    if (Q_prod<Demand) and (Q_prod+energy_stored>Demand): #Partial discharge
        
        energy_stored=energy_stored-(Demand-Q_prod)#New state of the storage
        Q_charg=0
        Q_discharg=(Demand-Q_prod)
        Q_prod_lim=Demand
        Q_useful=Demand
        SOC=100*energy_stored/energStorageMax
        Q_defocus=0
            
    if (Q_prod>=Demand): #Charging
        if ((Q_prod-Demand)+energy_stored)<energStorageMax: #Still room in the storage
            Q_useful=Q_prod
            energy_stored=energy_stored+(Q_prod-Demand) #New state of the storage
            Q_charg=(Q_prod-Demand)
            Q_discharg=0
            SOC=100*energy_stored/energStorageMax
            Q_defocus=0
            Q_prod_lim=Q_prod-Q_charg
        else: #No more room in the storage
           Q_charg=energStorageMax-energy_stored
           Q_useful=Demand+(energStorageMax-energy_stored)
           Q_discharg=0
           Q_defocus=Q_prod-Demand-Q_charg
           Q_prod_lim=Q_prod-Q_charg-Q_defocus
           energy_stored=energStorageMax #New state of the storage
           SOC=100*energy_stored/energStorageMax
           
    return [Q_prod_lim,Q_prod,Q_discharg,Q_charg,energy_stored,SOC,Q_defocus,Q_useful]

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

def outputFlowsHTF(Q_prod_lim,Cp_av,T_HX_out_K,T_process_out_K,flowDemand): 
    #HX simulation 
    flowToHx=Q_prod_lim/(Cp_av*(T_HX_out_K-T_process_out_K)) 
    if flowToHx>=flowDemand: 
        flowToHx=flowDemand #Macimum flow  
        T_HX_out_K=T_process_out_K+(Q_prod_lim/flowToHx)/Cp_av #Recalculate the oulet temperature 
         
    flowToMix=flowDemand-flowToHx 
    #Exit of the heat Echanger 
    [rho_toHX,Cp_toHX,k_toHX,Dv_toHX,Kv_toHX,thermalDiff_toHX,Prant_toHX]=thermalOil(T_HX_out_K)                     
    #Brach to mix 
    [rho_toMix,Cp_toMix,k_toMix,Dv_toMix,Kv_toMix,thermalDiff_toMix,Prant_toMix]=thermalOil(T_process_out_K)     
    #Mix 
    #T_av_HX_K=(T_process_out_K+T_HX_out_K)/2 #Ok when are more or less the same flowrate 
    T_av_HX_K=T_process_out_K*(flowToMix/flowDemand)+T_HX_out_K*(flowToHx/flowDemand) #When temperatures are very different             
    [rho_toProcess,Cp_toProcess,k_toProcess,Dv_toProcess,Kv_toProcess,thermalDiff_toProcess,Prant_toProcess]=thermalOil(T_av_HX_K)     
     
    if flowToHx==0: 
        T_toProcess_K=T_process_out_K 
    else: 
        T_toProcess_K=(flowToMix*Cp_toMix*T_process_out_K+flowToHx*Cp_toHX*T_HX_out_K)/(flowDemand*Cp_toProcess) 
 
    T_toProcess_C=T_toProcess_K-273            
    return [T_toProcess_C,flowToMix,T_toProcess_K,flowToMix,flowToHx] 
 
def outputFlowsWater(Q_prod_lim,P_op_Mpa,h_HX_out,h_process_out,T_process_out_K,flowDemand): 
    flowToHx=Q_prod_lim/(h_HX_out-h_process_out) 
    if flowToHx>=flowDemand: 
        flowToHx=flowDemand  #Maximum flow 
        h_HX_out=h_process_out+Q_prod_lim/flowToHx #Recalculate the oulet state 
     
    flowToMix=flowDemand-flowToHx 
    #Branch from HX to mix                         
    fromHXstate=IAPWS97(P=P_op_Mpa, h=h_HX_out) 
    #Mix 
    T_av_HX_K=(T_process_out_K+fromHXstate.T)/2 
    toProcessstate=IAPWS97(P=P_op_Mpa, T=T_av_HX_K) 
     
    if flowDemand==0: #If there's no demand then T_toProcss_K=0 
        T_toProcess_C=0 
    else: 
        T_toProcess_C=(flowToMix*h_process_out+flowToHx*h_HX_out)/(flowDemand*toProcessstate.cp) 
         
    T_toProcess_K=T_toProcess_C+273 
 
    return [T_toProcess_C,flowToMix,T_toProcess_K,flowToMix,flowToHx]

