# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 13:42:04 2016
Archivo que contiene las funciones de ITERACION

@author: Miguel Frasquet
"""
from Collector_modules.receivers import Rec_loss
from General_modules.func_General import thermalOil
from iapws import IAPWS97

def IT_flow (T_out_K,T_in_K,P_op_Mpa,temp_amb_K,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop):
    T_av_K=(T_in_K+T_out_K)/2
    average=IAPWS97(P=P_op_Mpa, T=T_av_K)
    Cp_av_KJkgK=average.cp
    
    Q_net_X=0
    for jj in range(1,202):
        if jj>=200: #Si no llegamos a convergencia después de 200 iteraciones paramos
            break
        if jj==1:
            err=99;
        else:
            err=(Q_net-Q_net_X)/Q_net_X
            Q_net_X=Q_net
        
        if abs(err)<=1e-4: #Si el error de convergencia es suficientemente bajo salimos del bucle
            break
        DELTA_T_loss=T_out_K-temp_amb_K
        [Q_loss_rec]=Rec_loss(REC_type,DELTA_T_loss,theta_i_rad,DNI) #W/m
    
        Q_net=DNI*IAM*Area-Q_loss_rec*n_coll_loop*Long #In W
    
        flow_rate_kgs=(DNI*IAM*Area)/((T_out_K-T_in_K)*Cp_av_KJkgK*1000)
        T_out_K=T_in_K+Q_net/(flow_rate_kgs*Cp_av_KJkgK*1000)
        
    return [flow_rate_kgs,T_out_K,Q_loss_rec]
    
def IT_temp(T_in_K,P_op_Mpa,temp_amb_K,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_rec,rho_optic_0):    
    T_outlet_KX=999
    for jj in range(1,202):
        if jj>=200: #Si no llegamos a convergencia después de 200 iteraciones paramos
            break
        if jj==1:
            err=99;
        else:
            err=(T_outlet_KX-T_outlet_K)/T_outlet_K
            T_outlet_KX=T_outlet_K
        
        if abs(err)<=1e-4: #Si el error de convergencia es suficientemente bajo salimos del bucle
            break
        
        T_av_K=(T_outlet_KX+T_in_K)/2
        average=IAPWS97(P=P_op_Mpa, T=T_av_K)
        Cp_av_KJkgK=average.cp
        
        DELTA_T_loss=T_outlet_KX-temp_amb_K
        [Q_loss_rec]=Rec_loss(REC_type,DELTA_T_loss,theta_i_rad,DNI)
        if Q_loss_rec<=0:
            Q_loss_rec=0
        
        gain=(DNI*Area*IAM*rho_optic_0-Q_loss_rec*n_coll_loop*Long)/(flow_rate_rec*Cp_av_KJkgK*1000) #In W
        if jj<2 and gain<0: #To avoid iteration errors at the very beigning
            gain=0
        T_outlet_K=T_in_K+gain
    Perd_termicas=Q_loss_rec*n_coll_loop*Long 
    return[T_outlet_K,Perd_termicas]

def IT_tempOil(T_in_K,temp_amb_K,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,flow_rate_rec,rho_optic_0):    
    T_outlet_KX=999
    for jj in range(1,202):
        if jj>=200: #Si no llegamos a convergencia después de 200 iteraciones paramos
            break
        if jj==1:
            err=99;
        else:
            err=(T_outlet_KX-T_outlet_K)/T_outlet_K
            T_outlet_KX=T_outlet_K
        
        if abs(err)<=1e-4: #Si el error de convergencia es suficientemente bajo salimos del bucle
            break
        
        T_av_K=(T_outlet_KX+T_in_K)/2
        [rho_av,Cp_av_KJkgK,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
        
        DELTA_T_loss=T_outlet_KX-temp_amb_K
        [Q_loss_rec]=Rec_loss(REC_type,DELTA_T_loss,theta_i_rad,DNI)
        if Q_loss_rec<=0:
            Q_loss_rec=0
        
        T_outlet_K=T_in_K+(DNI*Area*IAM*rho_optic_0-Q_loss_rec*n_coll_loop*Long)/(flow_rate_rec*Cp_av_KJkgK*1000) #In W 
    Perd_termicas=Q_loss_rec*n_coll_loop*Long 
    return[T_outlet_K,Perd_termicas]
    

def flow_calc (T_out_K,T_in_K,P_op_Mpa,temp_amb_K,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0):
    T_av_K=(T_in_K+T_out_K)/2
    average=IAPWS97(P=P_op_Mpa, T=T_av_K)
    Cp_av_KJkgK=average.cp
    
    DELTA_T_loss=T_out_K-temp_amb_K
    [Q_loss_rec]=Rec_loss(REC_type,DELTA_T_loss,theta_i_rad,DNI) #W/m
    flow_rate_kgs=(DNI*IAM*Area*rho_optic_0-Q_loss_rec*n_coll_loop*Long)/((T_out_K-T_in_K)*Cp_av_KJkgK*1000)

    Perd_termicas=Q_loss_rec*n_coll_loop*Long     
    return [flow_rate_kgs,Perd_termicas]

def flow_calcOil (T_out_K,T_in_K,Cp_av,temp_amb_K,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop,rho_optic_0):
    
    DELTA_T_loss=T_out_K-temp_amb_K
    [Q_loss_rec]=Rec_loss(REC_type,DELTA_T_loss,theta_i_rad,DNI) #W/m
    flow_rate_kgs=(DNI*IAM*Area*rho_optic_0-Q_loss_rec*n_coll_loop*Long)/((T_out_K-T_in_K)*Cp_av*1000)

    Perd_termicas=Q_loss_rec*n_coll_loop*Long
    if flow_rate_kgs<=0:
        flow_rate_kgs=0
        Perd_termicas=0
        
    return [flow_rate_kgs,Perd_termicas]
