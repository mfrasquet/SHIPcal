# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 11:51:50 2016
Función para obtener los IAMs a partir de ángulos

@author: miguel
"""
import numpy as np
import os

#INPUTS -------------------------------------

ang_target=79
IAM_type=0 # IAM_type=0 longitudinal; IAM_type=1 transversal
IAM_file="Fabian.csv"

# -------------------------------------------

def IAM_calc(ang_target,IAM_type,IAM_file):
    
    IAM_folder=os.path.dirname(os.path.dirname(__file__))+"/IAM_files/"  
    
    file_loc=IAM_folder+IAM_file
    IAM_raw = np.loadtxt(file_loc, delimiter=",")
    
    
    
    if IAM_type==0:
        column=1
    elif IAM_type==1:
        column=2
    else:
        exit(1)
        
    id_ang_inf=0
    while IAM_raw[id_ang_inf][0]<=ang_target:
        id_ang_inf=id_ang_inf+1
    
    ang_inf=(IAM_raw[id_ang_inf-1][0])
    id_ang_inf=id_ang_inf-1
    
    if abs(ang_inf-ang_target)<=0.0000001: #Considero que ambos valores son iguales
        IAM=IAM_raw[id_ang_inf][column]
    else: #Interpolamos
            IAMdata1=IAM_raw[id_ang_inf][column]
            IAMdata2=IAM_raw[id_ang_inf+1][column]
            IAM_dif=IAMdata2-IAMdata1
            ANGdata1=IAM_raw[id_ang_inf][0]
            ANGdata2=IAM_raw[id_ang_inf+1][0]
            ANG_dif=ANGdata2-ANGdata1
            IAM_unit=IAM_dif/ANG_dif
            
            dif_target=ang_target-ANGdata1
            incre_IAM_target=dif_target*IAM_unit
            
            IAM=IAMdata1+incre_IAM_target
    return [IAM]
    
[IAM]=IAM_calc(ang_target,IAM_type,IAM_file)   

        
        

