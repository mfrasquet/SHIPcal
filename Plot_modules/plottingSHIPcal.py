#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 19 14:53:58 2018

@author: miguel
"""

from matplotlib import pyplot as plt
from matplotlib.sankey import Sankey
import numpy as np
import pandas as pd
from iapws import IAPWS97
from General_modules.func_General import bar_MPa,thermalOil,moltenSalt
import io
import base64
import os


def SankeyPlot(sender,origin,lang,Production_max,Production_lim,Perd_term_anual,DNI_anual_irradiation,Area,num_loops,imageQlty,plotPath,**kwargs):

    #Proportions for Sankey
    
    raw_potential=DNI_anual_irradiation*Area*num_loops/1000 #MWh
    Utilization=(Production_max-Production_lim)/1000 #En Mwh
    Utilization_ratio=100*(Utilization/raw_potential) #Utilization ratio
    Thermal_loss=Perd_term_anual/1000 #Thermal loss over lim production
    Thermal_loss_ratio=100*(Thermal_loss/raw_potential) #Thermal loss over lim production
    
    Global_eff=100*(Production_lim/1000)/raw_potential
    
    Optic_loss_ratio=Global_eff-Thermal_loss_ratio-Utilization_ratio
    Production=Production_lim/1000 #en MWh
    
    sankeyDict={'Production':Production,'raw_potential':raw_potential,'Thermal_loss':Thermal_loss,'Utilization':Utilization}


    fig = plt.figure(figsize=(8, 8))
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
        
    if lang=="spa":
        ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],title="Diagrama Sankey producción solar")
    if lang=="eng":
        ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],title="Solar production - Sankey diagram")
    sankey = Sankey(ax=ax, unit=None)
    if lang=="spa":
        sankey.add(flows=[raw_potential/Production, -raw_potential/Production], #DNI_anual_irradiation/(Production*2) es lo que debería estar, se ha puesto el 1.1 del raw sólo por mostrarlo gráficamente mejor
               fc='#F2FA52',
               pathlengths = [0.95,0.375],
               patchlabel='\n\n\n'+(str(int(DNI_anual_irradiation))+' kWh/m2 - Radiación solar en el emplazamiento'),
               trunklength=2, 
               labels=['',' \n\n'+(str(int(raw_potential))+' MWh \n Radiación Solar*Area de colectores ('+str(int(Area*num_loops))+' m2)')],
               label='Radiación solar',
               orientations=[0, 0],
                rotation=-90)
    if lang=="eng":
        sankey.add(flows=[raw_potential/Production, -raw_potential/Production], #DNI_anual_irradiation/(Production*2) es lo que debería estar, se ha puesto el 1.1 del raw sólo por mostrarlo gráficamente mejor
            fc='#F2FA52',
            pathlengths = [0.95,0.375],
           patchlabel='\n\n\n'+(str(int(DNI_anual_irradiation))+' kWh/m2 - Solar radiation at the location'),
           trunklength=2, 
           labels=['',' \n\n'+(str(int(raw_potential))+' MWh \n Solar Radiation*Area of collectors ('+str(int(Area*num_loops))+' m2)')],
           label='Solar radiation',
           orientations=[0, 0],
            rotation=-90)
    if lang=="spa":    
        sankey.add(flows=[raw_potential/Production,-(raw_potential-Production-Thermal_loss-Utilization)/Production,-Utilization/Production,-Thermal_loss/Production, -Production/Production],
               fc='#FA9E52',
               pathlengths = [3,0.6,0.6,0.3,0.3],       
               label='Instalación solar',
               labels=['', (''+str(round(raw_potential-Utilization-Production-Thermal_loss,1))+' MWh - No puede concentrarse'),('                                                                              '+str(round(Utilization,1))+' MWh - No puede utilizarse por la industria \n                                                          (no hay consumo cuando se produce)'),('\n                                             '+str(round(Thermal_loss,1))+' MWh - Pérdidas térmicas'), '         '+(str(round(Production,1))+' MWh - Producción neta')],
               orientations=[0, 1,1,1, 0],rotation=-90, prior=0, connect=(1, 0))
    if lang=="eng":
        sankey.add(flows=[raw_potential/Production,-(raw_potential-Production-Thermal_loss-Utilization)/Production,-Utilization/Production,-Thermal_loss/Production, -Production/Production],
               fc='#FA9E52',
               pathlengths = [3,0.6,0.6,0.3,0.3],       
               label='Solar plant',
               labels=['', (''+str(round(raw_potential-Utilization-Production-Thermal_loss,1))+' MWh - Spillage'),('                                                                    '+str(round(Utilization,1))+' MWh - Industry cannot use the energy \n                                                          (There is no demand when it is produced)'),('\n                                             '+str(round(Thermal_loss,1))+' MWh - Thermal losses'), '         '+(str(round(Production,1))+' MWh - Net production')],
               orientations=[0, 1,1,1, 0],rotation=-90, prior=0, connect=(1, 0))
 
        
    diagrams = sankey.finish()
    plt.legend(loc='upper left')
    plt.tight_layout()
       

    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64,sankeyDict
    if origin==-1:
        fig.savefig(str(plotPath)+'Sankey.png', format='png', dpi=imageQlty)              
        return 0,sankeyDict
    if origin==0:
        return 0,sankeyDict 
    
def mollierPlotST(sender,origin,lang,type_integration,in_s,out_s,T_in_flag,T_in_C,T_in_C_AR,T_out_C,outProcess_s,T_out_process_C,P_op_bar,x_design,plotPath,imageQlty,**kwargs):
    P_op_Mpa=P_op_bar/10
    sat_liq=IAPWS97(P=P_op_Mpa, x=0)
    sat_vap=IAPWS97(P=P_op_Mpa, x=1)
    mollier=pd.read_csv(os.path.dirname(__file__)+'/mollierWater.csv',sep=',',encoding = "ISO-8859-1",header=None)  

    processEntropy=[]
    processEntropy.append(in_s)
    if type_integration=="SL_S_PD" or type_integration=="SL_S_PDS":
        processEntropy.append(sat_liq.s)
    processEntropy.append(out_s)
    processTemperature=[]
    if T_in_flag==1:
        processTemperature.append(T_in_C)
    else:
        processTemperature.append(np.average(T_in_C_AR))
    if type_integration=="SL_S_PD" or type_integration=="SL_S_PDS":
        processTemperature.append(sat_liq.T-273)
    processTemperature.append(T_out_C)
    
    
    if type_integration=="SL_S_FWS" or type_integration=="SL_S_FW":
        processEntropy2=[]
        processTemperature2=[]
        processEntropy2.append(out_s)
        processEntropy2.append(sat_liq.s)
        processEntropy2.append(sat_vap.s)
        processTemperature2.append(T_out_C)
        processTemperature2.append(sat_vap.T-273)
        processTemperature2.append(sat_vap.T-273)
    if type_integration=="SL_L_RF":
        processEntropy2=[]
        processTemperature2=[]
        processEntropy2.append(out_s)
        processEntropy2.append(outProcess_s)
        processTemperature2.append(T_out_C)
        processTemperature2.append(T_out_process_C)
    if type_integration=="SL_S_PD" or type_integration=="SL_S_PDS":
        processEntropy2=[]
        processTemperature2=[]
        processEntropy2.append(out_s)
        processEntropy2.append(outProcess_s)
        processTemperature2.append(T_out_C)
        processTemperature2.append(T_out_C)

    i=0
    s=0.1
    s_max=8
    s_step=0.1
    P_isobar=P_op_bar #bar
    isobar=pd.DataFrame(np.zeros((int((s_max-s)/s_step),3)), columns=["T","h","s"])
    while (s<s_max):
       stateIsobar=IAPWS97(P=bar_MPa(P_isobar), s=s)
       isobar["T"][i]=stateIsobar.T-273
       isobar["h"][i]=stateIsobar.h
       isobar["s"][i]=s
       s=s+s_step
       i=i+1
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    plt.text(7.5, 350, str(int(P_isobar))+"bar", size=10, color='k', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
    if lang=="spa":    
        plt.title("Diagrama T-s en una fila de colectores") 
    if lang=="eng":
        plt.title("T-s diagram in one array of solar collectors") 
    plt.plot(processEntropy,processTemperature, color='r',lw=3,markersize=50,zorder=10 )
    if type_integration=="SL_S_FWS" or type_integration=="SL_S_FW":
        plt.plot(processEntropy2,processTemperature2, color='m',lw=2,markersize=50,zorder=10 )
    if type_integration=="SL_L_RF":
        plt.plot(processEntropy2,processTemperature2, color='m',lw=2,markersize=50,zorder=10 )
    if type_integration=="SL_S_PD" or type_integration=="SL_S_PDS":
        plt.plot(processEntropy2,processTemperature2, color='m',lw=2,markersize=50,zorder=10 )
    plt.plot(mollier[1],mollier[0],':',lw=2)
    plt.plot(isobar["s"],isobar["T"])
    if lang=="spa":
        if T_in_flag==1:
            plt.text(processEntropy[0]-1.5, processTemperature[0], "Entrada "+str(int(T_in_C))+"ºC", size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        else:
            plt.text(processEntropy[0]-1.5, processTemperature[0], "Entrada "+str(int(np.average(T_in_C_AR)))+"ºC", size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
       
    if lang=="eng":
        if T_in_flag==1:
            plt.text(processEntropy[0]-1.5, processTemperature[0], "Input "+str(int(T_in_C))+"ºC", size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        else:
            plt.text(processEntropy[0]-1.5, processTemperature[0], "Input "+str(int(np.average(T_in_C_AR)))+"ºC", size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
   
    if type_integration=="SL_S_PD" or type_integration=="SL_S_PDS":
        if lang=="spa":
            plt.text(processEntropy[2]-1, processTemperature[2]+20, "Salida "+str(int(P_op_bar))+"bar x="+str(x_design), size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
            plt.text(processEntropy2[1], processTemperature2[1]-15, "Salida "+str(int(P_op_bar))+"bar Sat.", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        if lang=="eng":
            plt.text(processEntropy[2]-1, processTemperature[2]+20, "Output "+str(int(P_op_bar))+"bar x="+str(x_design), size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
            plt.text(processEntropy2[1], processTemperature2[1]-15, "Output "+str(int(P_op_bar))+"bar Sat.", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
 
    else:
        if lang=="spa":
            plt.text(processEntropy[1]-1.3, processTemperature[1]+10, "Salida "+str(int(T_out_C))+"ºC", size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        if lang=="eng":
            plt.text(processEntropy[1]-1.3, processTemperature[1]+10, "Output "+str(int(T_out_C))+"ºC", size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   

    if type_integration=="SL_S_FWS" or type_integration=="SL_S_FW":
        if lang=="spa":
            plt.text(processEntropy2[2], processTemperature2[2]+20, "Salida "+str(int(P_op_bar))+"bar Sat.", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        if lang=="eng":
            plt.text(processEntropy2[2], processTemperature2[2]+20, "Output "+str(int(P_op_bar))+"bar Sat.", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
            
    if type_integration=="SL_L_RF":
        if lang=="spa":
            plt.text(processEntropy2[1]-1.3, processTemperature2[1]+10, "Salida "+str(int(T_out_process_C))+"ºC", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        if lang=="eng":
            plt.text(processEntropy2[1]-1.3, processTemperature2[1]+10, "Output "+str(int(T_out_process_C))+"ºC", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   

    if lang=="spa":
        plt.text(-2,200, "Liquido" , size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        plt.text(4.5,20, "Liquido + Vapor", size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        plt.text(10,200, "Vapor", size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
    #    plt.scatter(modules["s"],modules["T"])
        
        plt.xlabel(r'Entropía (kJ/K/kg)')
        plt.ylabel(r'Temperatura (C)')
    if lang=="eng":
        plt.text(-2,200, "Liquid" , size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        plt.text(4.5,20, "Liquid + Steam", size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        plt.text(10,200, "Steam", size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
    #    plt.scatter(modules["s"],modules["T"])
        
        plt.xlabel(r'Entropy (kJ/K/kg)')
        plt.ylabel(r'Temperature (C)')
    axes = plt.gca()
    axes.set_ylim([0,400])
    axes.set_xlim([-3,11])
        
    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin== -1:
        fig.savefig(str(plotPath)+'Mollier.png', format='png', dpi=imageQlty) #Save image for the report for the report
       

def  mollierPlotSH(sender,origin,lang,type_integration,h_in,h_out,hProcess_out,outProcess_h,in_s,out_s,T_in_flag,T_in_C,T_in_C_AR,T_out_C,outProcess_s,T_out_process_C,P_op_bar,x_design,plotPath,imageQlty,**kwargs):
    mollier=pd.read_csv(os.path.dirname(__file__)+'/mollierWater.csv',sep=',',encoding = "ISO-8859-1",header=None)  

    P_op_Mpa=P_op_bar/10
    sat_liq=IAPWS97(P=P_op_Mpa, x=0)
    sat_vap=IAPWS97(P=P_op_Mpa, x=1)
    
    processEntropy=[]
    processEntropy.append(in_s)
    if type_integration=="SL_S_PD" or type_integration=="SL_S_PDS":
        processEntropy.append(sat_liq.s)
    processEntropy.append(out_s)

    
    
    processEnthalpy=[]
    processEnthalpy.append(h_in)
    if type_integration=="SL_S_PD" or type_integration=="SL_S_PDS":
        processEnthalpy.append(sat_liq.h)
    processEnthalpy.append(h_out)
    
    
    if type_integration=="SL_S_FWS" or type_integration=="SL_S_FW":
        processEntropy2=[]
        processEnthalpy2=[]
        processEntropy2.append(out_s)
        processEntropy2.append(sat_vap.s)
        processEnthalpy2.append(h_out)
        processEnthalpy2.append(sat_vap.h)
    if type_integration=="SL_L_RF":
        processEntropy2=[]
        processEnthalpy2=[]
        processEntropy2.append(out_s)
        processEntropy2.append(outProcess_s)
        processEnthalpy2.append(h_out)
        processEnthalpy2.append(hProcess_out)
    if type_integration=="SL_S_PD" or type_integration=="SL_S_PDS":
        processEntropy2=[]
        processEnthalpy2=[]
        processEntropy2.append(out_s)
        processEntropy2.append(outProcess_s)
        processEnthalpy2.append(h_out)
        processEnthalpy2.append(outProcess_h)
    
    i=0
    s=0.1
    s_max=8
    s_step=0.1
    P_isobar=P_op_bar #bar
    isobar=pd.DataFrame(np.zeros((int((s_max-s)/s_step),3)), columns=["T","h","s"])
    while (s<s_max):
       stateIsobar=IAPWS97(P=bar_MPa(P_isobar), s=s)
       isobar["h"][i]=stateIsobar.h
       isobar["s"][i]=s
       s=s+s_step
       i=i+1
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    plt.text(5, IAPWS97(P=bar_MPa(P_isobar),s=5).h-500, str(int(P_isobar))+"bar", size=10, color='k', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
    if lang=="spa":        
        plt.title("Diagrama h-s en una fila de colectores")
    if lang=="eng":        
        plt.title("H-s diagram in one array of solar collectors")    
    if type_integration=="SL_S_FWS" or type_integration=="SL_S_FW":
        plt.plot(processEntropy2,processEnthalpy2, color='m',lw=2,markersize=50,zorder=10 )
    if type_integration=="SL_L_RF":
        plt.plot(processEntropy2,processEnthalpy2, color='m',lw=2,markersize=50,zorder=10 )  
    if type_integration=="SL_S_PD" or type_integration=="SL_S_PDS":
        plt.plot(processEntropy2,processEnthalpy2, color='m',lw=2,markersize=50,zorder=10 )         
    plt.plot(processEntropy,processEnthalpy, color='r',lw=3,markersize=50,zorder=10 )
    plt.plot(mollier[1],mollier[2],':',lw=2)
    plt.plot(isobar["s"],isobar["h"])
    if lang=="spa":
        plt.text(processEntropy[0]-1.8, processEnthalpy[0]+100, "Entrada "+str(int(h_in))+" kJ/kg", size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
    if lang=="eng":
        plt.text(processEntropy[0]-1.8, processEnthalpy[0]+100, "Inlet "+str(int(h_in))+" kJ/kg", size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
    
    if type_integration=="SL_S_PD" or type_integration=="SL_S_PDS":
        if lang=="spa":
            plt.text(processEntropy[2]+1.8, processEnthalpy[2]-100, "Salida "+str(int(P_op_bar))+"bar x="+str(x_design), size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
            plt.text(processEntropy2[1]+1.8, processEnthalpy2[1]-100, "Salida "+str(int(P_op_bar))+"bar Sat.", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        if lang=="eng":
            plt.text(processEntropy[2]+1.8, processEnthalpy[2]-100, "Output "+str(int(P_op_bar))+"bar x="+str(x_design), size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
            plt.text(processEntropy2[1]+1.8, processEnthalpy2[1]-100, "Output "+str(int(P_op_bar))+"bar Sat.", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)    
    else:
        if lang=="spa":
            plt.text(processEntropy[1]-1.5, processEnthalpy[1]+150, "Salida "+str(int(h_out))+" kJ/kg", size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        if lang=="eng":
            plt.text(processEntropy[1]-1.5, processEnthalpy[1]+150, "Output "+str(int(h_out))+" kJ/kg", size=10, color='r', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   

    if type_integration=="SL_S_FWS" or type_integration=="SL_S_FW":
        if lang=="spa":
            plt.text(processEntropy2[1]+1.8, processEnthalpy2[1]-100, "Salida "+str(int(P_op_bar))+"bar Sat.", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
            plt.text(processEntropy2[1]+1.8, processEnthalpy2[1]-300, "Salida "+str(int(sat_vap.h))+" kJ/kg", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        if lang=="eng":
            plt.text(processEntropy2[1]+1.8, processEnthalpy2[1]-100, "Output "+str(int(P_op_bar))+"bar Sat.", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
            plt.text(processEntropy2[1]+1.8, processEnthalpy2[1]-300, "Output "+str(int(sat_vap.h))+" kJ/kg", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   

    if type_integration=="SL_L_RF":
        if lang=="spa":
            plt.text(processEntropy2[1]-1.5, processEnthalpy2[1]+150, "Salida "+str(int(hProcess_out))+" kJ/kg", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        if lang=="eng":
            plt.text(processEntropy2[1]-1.5, processEnthalpy2[1]+150, "Output "+str(int(hProcess_out))+" kJ/kg", size=10, color='m', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   

    if lang=="spa": 
        plt.text(-1,1500, "Liquido" , size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        plt.text(4.5,200, "Liquido + Vapor", size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        plt.text(10,2000, "Vapor", size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
    #    plt.scatter(modules["s"],modules["T"])
        
        plt.xlabel(r'Entropía (kJ/K/kg)')
        plt.ylabel(r'Entalpía (kJ/Kg)')
    if lang=="eng":
        plt.text(-1,1500, "Liquid" , size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        plt.text(4.5,200, "Liquid + Steam", size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
        plt.text(10,2000, "Steam", size=10, color='b', ha='center', va='center', horizontalalignment='center', verticalalignment='center', rotation= 0)   
    #    plt.scatter(modules["s"],modules["T"])
        
        plt.xlabel(r'Entropy (kJ/K/kg)')
        plt.ylabel(r'Enthalpy (kJ/Kg)')
        
    axes = plt.gca()
    axes.set_ylim([0,3000])
    axes.set_xlim([-3,11])
   
    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'Mollier2.png', format='png', dpi=imageQlty) #Save for the report
        
    
def thetaAnglesPlot(sender,origin,step_sim,steps_sim,theta_i_deg,theta_transv_deg,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    fig.suptitle('Ángulos theta', fontsize=14, fontweight='bold')
    ax1 = fig.add_subplot(111)  
    ax1 .plot(step_sim, theta_i_deg,'.r-',label="Ang_incidencia")
    ax1 .plot(step_sim, theta_transv_deg,'.b-',label="Incidencia_transversal")
    ax1 .axhline(y=0,xmin=0,xmax=steps_sim,c="blue",linewidth=0.5,zorder=0)
    ax1.set_xlabel('Simulación (hora del año)')
    ax1.set_ylabel('Grados')
    plt.legend( loc='upper left', borderaxespad=0.)
    
    if origin==-2 or origin == -3:     
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'tetha.png', format='png', dpi=imageQlty)

def IAMAnglesPlot(sender,origin,step_sim,IAM_long,IAM_t,IAM,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    fig.suptitle('IAMs', fontsize=14, fontweight='bold')
    ax2 = fig.add_subplot(111)         
    ax2 .plot(step_sim, IAM_long,'.-',color = 'b',label="IAM_long")
    ax2 .plot(step_sim, IAM_t,'.-',color = 'r',label="IAM_transv")
    ax2 .plot(step_sim, IAM,'.-',color = '#39B8E3',label="IAM")
    ax2.set_xlabel('Simulación (hora del año)')
    ax2.set_ylabel('Grados')
    plt.legend(loc='upper left', borderaxespad=0.)
    
    if origin==-2 or origin == -3:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'IAM.png', format='png', dpi=imageQlty)
    
def demandVsRadiation(sender,origin,lang,step_sim,Demand,Q_prod,Q_prod_lim,Q_prod_rec,steps_sim,DNI,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa": 
        fig.suptitle('Demanda vs Radiación solar', fontsize=14, fontweight='bold')
        ax1 = fig.add_subplot(111)  
        ax1 .plot(step_sim, Demand,'.k-',label="Demanda")
        ax1 .plot(step_sim, Q_prod,'.r-',label="Produccion solar total")
        ax1 .plot(step_sim, Q_prod_lim,'.b-',label="Produccion util")
        ax1 .plot(step_sim, Q_prod_rec,'.g-',label="Produccion Rec")
        ax1 .axhline(y=0,xmin=0,xmax=steps_sim,c="blue",linewidth=0.5,zorder=0)
        ax1.set_xlabel('Simulación (hora del año)')
        ax1.set_ylabel('Demanda - kWh',color="blue")
        ax1.set_ylim([0,max(np.max(Q_prod),np.max(Demand))*1.2])
        plt.legend(loc='upper left', borderaxespad=0.)
        ax2 = ax1.twinx()          
        ax2 .plot(step_sim, DNI,'.-',color = 'orange',label="DNI")
        ax2.set_ylabel('Radiación solar - W/m2',color='red')
        ax2.set_ylim([0,np.max(DNI)*1.2])
        plt.legend(loc='upper right', borderaxespad=0.)
    if lang=="eng":
        fig.suptitle('Demand vs Solar Radiation', fontsize=14, fontweight='bold')
        ax1 = fig.add_subplot(111)  
        ax1 .plot(step_sim, Demand,'.k-',label="Demand")
        ax1 .plot(step_sim, Q_prod,'.r-',label="Total solar production")
        ax1 .plot(step_sim, Q_prod_lim,'.b-',label="Net production")
        ax1 .plot(step_sim, Q_prod_rec,'.g-',label="Production Rec")
        ax1 .axhline(y=0,xmin=0,xmax=steps_sim,c="blue",linewidth=0.5,zorder=0)
        ax1.set_xlabel('simulation time (hour of the year)')
        ax1.set_ylabel('Demand - kWh',color="blue")
        ax1.set_ylim([0,np.max(Demand)*1.2])
        plt.legend(loc='upper left', borderaxespad=0.)
        ax2 = ax1.twinx()          
        ax2 .plot(step_sim, DNI,'.-',color = 'orange',label="DNI")
        ax2.set_ylabel('Solar Radiaton - W/m2',color='red')
        plt.legend(loc='upper right', borderaxespad=0.)
    
    if origin==-2 or origin == -3:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'demandProduction.png', format='png', dpi=imageQlty)

def rhoTempPlotSalt(sender,origin,lang,T_out_C,plotPath,imageQlty,**kwargs):
    rhoList=[]
    CpList=[]
    T_step=[]
    for T in range(100+273,600+273,5):
        T_step.append(T-273)
        [rho,Cp,k,Dv]=moltenSalt(T)
        rhoList.append(rho)
        CpList.append(Cp)
    
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa":     
        fig.suptitle('Propiedades de las sales fundidas', fontsize=14, fontweight='bold')
        ax1 = fig.add_subplot(111)  
        ax1 .plot(np.arange(len(rhoList)), rhoList,'.k-',label="Densidad")
        [rho,Cp,k,Dv]=moltenSalt(T_out_C+273)
        plt .hlines(y=rho,xmin=0,xmax=min(range(len(rhoList)), key=lambda i: abs(rhoList[i]-rho)),color="#362510",linewidth=1,zorder=0)
        plt .axvline(x=min(range(len(rhoList)), key=lambda i: abs(rhoList[i]-rho)),c="r")  
        ax1.set_xlabel('Temperatura ºC')
        ax1.set_ylabel('Densidad - kg/m3')
        ax2 = ax1.twinx()          
        ax2 .plot(np.arange(len(rhoList)), CpList,'.b-',label="Calor específico")
        ax2.set_ylabel('Calor Específico - KJ/kgK', color="blue")
        plt.xticks(list(np.arange(len(rhoList)))[1::8], T_step[1::8])  
        plt .hlines(y=Cp,xmin=min(range(len(CpList)), key=lambda i: abs(CpList[i]-Cp)),xmax=len(T_step),color="blue",linewidth=1,zorder=0)     
    if lang=="eng":
        fig.suptitle('Molten Salt properties', fontsize=14, fontweight='bold')
        ax1 = fig.add_subplot(111)  
        ax1 .plot(np.arange(len(rhoList)), rhoList,'.k-',label="Density")
        [rho,Cp,k,Dv]=moltenSalt(T_out_C+273)
        plt .hlines(y=rho,xmin=0,xmax=min(range(len(rhoList)), key=lambda i: abs(rhoList[i]-rho)),color="#362510",linewidth=1,zorder=0)
        plt .axvline(x=min(range(len(rhoList)), key=lambda i: abs(rhoList[i]-rho)),c="r")  
        ax1.set_xlabel('Temperature ºC')
        ax1.set_ylabel('Density - kg/m3')
        ax2 = ax1.twinx()          
        ax2 .plot(np.arange(len(rhoList)), CpList,'.b-',label="Specific heat")
        ax2.set_ylabel('Specific heat - lKJ/kgK', color="blue")
        plt.xticks(list(np.arange(len(rhoList)))[1::8], T_step[1::8])  
        plt .hlines(y=Cp,xmin=min(range(len(CpList)), key=lambda i: abs(CpList[i]-Cp)),xmax=len(T_step),color="blue",linewidth=1,zorder=0)     

    
    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'Salt.png', format='png', dpi=imageQlty)    

def rhoTempPlotOil(sender,origin,lang,T_out_C,plotPath,imageQlty,**kwargs):
    rhoList=[]
    CpList=[]
    T_step=[]
    for T in range(-20+273,320+273,5):
        T_step.append(T-273)
        [rho,Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T)
        rhoList.append(rho)
        CpList.append(Cp)
    
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa":     
        fig.suptitle('Propiedades del Aceite térmico', fontsize=14, fontweight='bold')
        ax1 = fig.add_subplot(111)  
        ax1 .plot(np.arange(len(rhoList)), rhoList,'.k-',label="Densidad")
        [rho,Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_out_C+273)
        plt .hlines(y=rho,xmin=0,xmax=min(range(len(rhoList)), key=lambda i: abs(rhoList[i]-rho)),color="#362510",linewidth=1,zorder=0)
        plt .axvline(x=min(range(len(rhoList)), key=lambda i: abs(rhoList[i]-rho)),c="r")  
        ax1.set_xlabel('Temperatura ºC')
        ax1.set_ylabel('Densidad - kg/m3')
        ax2 = ax1.twinx()          
        ax2 .plot(np.arange(len(rhoList)), CpList,'.b-',label="Calor específico")
        ax2.set_ylabel('Calor Específico - KJ/kgK', color="blue")
        plt.xticks(list(np.arange(len(rhoList)))[1::8], T_step[1::8])  
        plt .hlines(y=Cp,xmin=min(range(len(CpList)), key=lambda i: abs(CpList[i]-Cp)),xmax=len(T_step),color="blue",linewidth=1,zorder=0)     
    if lang=="eng":
        fig.suptitle('Thermal Oil properties', fontsize=14, fontweight='bold')
        ax1 = fig.add_subplot(111)  
        ax1 .plot(np.arange(len(rhoList)), rhoList,'.k-',label="Density")
        [rho,Cp,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_out_C+273)
        plt .hlines(y=rho,xmin=0,xmax=min(range(len(rhoList)), key=lambda i: abs(rhoList[i]-rho)),color="#362510",linewidth=1,zorder=0)
        plt .axvline(x=min(range(len(rhoList)), key=lambda i: abs(rhoList[i]-rho)),c="r")  
        ax1.set_xlabel('Temperature ºC')
        ax1.set_ylabel('Density - kg/m3')
        ax2 = ax1.twinx()          
        ax2 .plot(np.arange(len(rhoList)), CpList,'.b-',label="Specific heat")
        ax2.set_ylabel('Specific heat - KJ/kgK', color="blue")
        plt.xticks(list(np.arange(len(rhoList)))[1::8], T_step[1::8])  
        plt .hlines(y=Cp,xmin=min(range(len(CpList)), key=lambda i: abs(CpList[i]-Cp)),xmax=len(T_step),color="blue",linewidth=1,zorder=0)     

    
    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'Oil.png', format='png', dpi=imageQlty)

def viscTempPlotSalt(sender,origin,lang,T_out_C,plotPath,imageQlty,**kwargs):
    DvList=[]
    T_step=[]
    for T in range(100+273,600+273,5):
        T_step.append(T-273)
        [rho,Cp,k,Dv]=moltenSalt(T)
        DvList.append(Dv*1e3)
    
    DvList=DvList[4:]
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa":    
        fig.suptitle('Viscosidad de las sales fudidas', fontsize=14, fontweight='bold')
        
        ax1 = fig.add_subplot(111)  
        ax1 .plot(np.arange(len(DvList)), DvList,'.k-',label="Viscosidad dinámica")
        
        [rho,Cp,k,Dv]=moltenSalt(T_out_C+273)
        plt .hlines(y=Dv*1e3,xmin=0,xmax=min(range(len(DvList)), key=lambda i: abs(DvList[i]-Dv*1e3)),color="#362510",linewidth=1,zorder=0)
        plt .axvline(x=min(range(len(DvList)), key=lambda i: abs(DvList[i]-Dv*1e3)),c="r")  
        ax1.set_xlabel('Temperatura ºC')
        ax1.set_ylabel('Viscosidad dinámica*1e3  - Ns/m2')
        ax1.set_yscale('log')
        plt.xticks(list(np.arange(len(T_step)))[1::8], T_step[1::8]) 
     
    if lang=="eng":
        fig.suptitle('Molten Salt Viscosity', fontsize=14, fontweight='bold')
        
        ax1 = fig.add_subplot(111)  
        ax1 .plot(np.arange(len(DvList)), DvList,'.k-',label="Dynamic viscosity")
        
        [rho,Cp,k,Dv]=moltenSalt(T_out_C+273)
        plt .hlines(y=Dv*1e3,xmin=0,xmax=min(range(len(DvList)), key=lambda i: abs(DvList[i]-Dv*1e3))+4,color="#362510",linewidth=1,zorder=0)
        plt .axvline(x=min(range(len(DvList)), key=lambda i: abs(DvList[i]-Dv*1e3))+4,c="r")  
        ax1.set_xlabel('Temperature ºC')
        ax1.set_ylabel('Dynamic viscosity*1e3  - Ns/m2')
        ax1.set_yscale('log')
           
    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'Salt2.png', format='png', dpi=imageQlty)
        
def viscTempPlotOil(sender,origin,lang,T_out_C,plotPath,imageQlty,**kwargs):
    DvList=[]
    KvList=[]
    T_step=[]
    for T in range(-20+273,320+273,5):
        T_step.append(T-273)
        [rho,Cp,k,Dv,Kv,thermalDiff,Prant]=thermalOil(T)
        DvList.append(Dv*1e3)
        KvList.append(Kv*1e6)
    
    DvList=DvList[4:]
    KvList=KvList[4:]
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa":    
        fig.suptitle('Viscosidad del Aceite térmico', fontsize=14, fontweight='bold')
        
        ax1 = fig.add_subplot(111)  
        ax1 .plot(np.arange(len(DvList)), DvList,'.k-',label="Viscosidad dinámica")
        
        [rho,Cp,k,Dv,Kv,thermalDiff,Prant]=thermalOil(T_out_C+273)
        plt .hlines(y=Dv*1e3,xmin=0,xmax=min(range(len(DvList)), key=lambda i: abs(DvList[i]-Dv*1e3))+4,color="#362510",linewidth=1,zorder=0)
        plt .axvline(x=min(range(len(DvList)), key=lambda i: abs(DvList[i]-Dv*1e3))+4,c="r")  
        ax1.set_xlabel('Temperatura ºC')
        ax1.set_ylabel('Viscosidad dinámica*1e3  - Ns/m2')
        ax1.set_yscale('log')
        ax2 = ax1.twinx()          
        ax2 .plot(np.arange(len(KvList)), KvList,'.b-',label="Viscosidad cinemática")
        ax2.set_ylabel('Viscosidad cinemática*1e6 - m2/s', color="blue")
        ax2.set_yscale('log')
        plt.xticks(list(np.arange(len(T_step)))[1::8], T_step[1::8])  
        plt .hlines(y=Kv*1e6,xmin=min(range(len(DvList)), key=lambda i: abs(DvList[i]-Dv*1e3))+4,xmax=len(T_step),color="blue",linewidth=1,zorder=0)     
    if lang=="eng":
        fig.suptitle('Thermal Oil Viscosity', fontsize=14, fontweight='bold')
        
        ax1 = fig.add_subplot(111)  
        ax1 .plot(np.arange(len(DvList)), DvList,'.k-',label="Dynamic viscosity")
        
        [rho,Cp,k,Dv,Kv,thermalDiff,Prant]=thermalOil(T_out_C+273)
        plt .hlines(y=Dv*1e3,xmin=0,xmax=min(range(len(DvList)), key=lambda i: abs(DvList[i]-Dv*1e3))+4,color="#362510",linewidth=1,zorder=0)
        plt .axvline(x=min(range(len(DvList)), key=lambda i: abs(DvList[i]-Dv*1e3))+4,c="r")  
        ax1.set_xlabel('Temperature ºC')
        ax1.set_ylabel('Dynamic viscosity*1e3  - Ns/m2')
        ax1.set_yscale('log')
        ax2 = ax1.twinx()          
        ax2 .plot(np.arange(len(KvList)), KvList,'.b-',label="Kinematic viscosity")
        ax2.set_ylabel('Kinematic viscosity*1e6 - m2/s', color="blue")
        ax2.set_yscale('log')
        plt.xticks(list(np.arange(len(T_step)))[1::8], T_step[1::8])  
        plt .hlines(y=Kv*1e6,xmin=min(range(len(DvList)), key=lambda i: abs(DvList[i]-Dv*1e3))+4,xmax=len(T_step),color="blue",linewidth=1,zorder=0)     

    
    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'Oil2.png', format='png', dpi=imageQlty)
        
def flowRatesPlot(sender,origin,step_sim,steps_sim,flow_rate_kgs,flow_rate_rec,num_loops,flowDemand,flowToHx,flowToMix,m_dot_min_kgs,T_in_K,T_toProcess_C,T_out_K,T_alm_K,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    fig.suptitle('Caudales & temperaturas', fontsize=14, fontweight='bold')
    ax1 = fig.add_subplot(111)  
    ax1 .plot(step_sim, flow_rate_kgs,'m:',label="Caudal solar array")
    ax1 .plot(step_sim, flow_rate_rec,'g:',label="Caudal recirculación array")    
    ax1 .plot(step_sim, flow_rate_kgs*num_loops,'.m-',label="Caudal solar SF")
    ax1 .plot(step_sim, flow_rate_rec*num_loops,'.g-',label="Caudal recirculación SF")    
    ax1 .plot(step_sim, flowDemand,'.k-',label="Caudal demanda")
    ax1 .plot(step_sim, flowToHx,'.y-',label="Caudal flowToHx")
    ax1 .plot(step_sim, flowToMix,'.-',color='#6BD703',label="Caudal flowToMix")
    ax1 .axhline(y=m_dot_min_kgs,xmin=0,xmax=steps_sim,c="black",linewidth=0.5,zorder=0)
    ax1.set_ylim([0,(np.max(flow_rate_kgs*num_loops))*1.1])
    ax1.set_xlabel('Simulación (hora del año)')
    ax1.set_ylabel('Caudal - kg/s')
    plt.legend(bbox_to_anchor=(1.15, .5), loc=2, borderaxespad=0.)
    ax2 = ax1.twinx()          
    ax2 .plot(step_sim, T_in_K-273,'-',color = '#1F85DE',label="Temp_in Solar")
    ax2 .plot(step_sim, T_toProcess_C,'-',color = 'brown',label="Tem to Process")
    ax2 .plot(step_sim, T_out_K-273,'-',color = 'red',label="Temp_out Solar")
    ax2 .plot(step_sim, T_alm_K-273,':',color = 'orange',label="Temp_alm")
    ax2.set_ylabel('Temp - C')
    ax2.set_ylim([0,(np.max([np.max(T_toProcess_C)+273,np.max(T_out_K)])-273)*1.1])
    plt.legend(bbox_to_anchor=(1.15, 1), loc=2, borderaxespad=0.)    
            
#    output1=pd.DataFrame(flow_rate_kgs)
#    output1.columns=['Flow_rate']
#    output2=pd.DataFrame(T_in_K)
#    output2.columns=['T_in_K']
#    output3=pd.DataFrame(T_out_K)
#    output3.columns=['T_out_K']
#    output_excel_FlowratesTemps=pd.concat([output1,output2,output3], axis=1)
    
    if origin==-2 or origin == -3:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'flowrates.png', format='png', dpi=imageQlty)
    
def prodWinterPlot(sender,origin,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
        
    if lang=="spa": 
        fig.suptitle('Producción solar primera semana Enero', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)
        
        ax1 .plot(np.arange(167), DNI[0:167],color='#CA6A16',linestyle='solid',label="Radiación solar")
        ax1.set_xlabel('simulación (hora del año)')
        ax1.set_ylabel('Radiación Solar - W/m2')
        ax1.set_ylim([0,1200])
        plt.legend(loc='upper left', borderaxespad=0.,frameon=False)
        ax2 = ax1.twinx()   
        ax2.fill_between( np.arange(167), Demand[0:167], color="grey", alpha=0.2,label="Demanda")
        ax2 .plot(np.arange(167), Demand[0:167],'.-',color = '#362510',label="Demanda")
        if sender =='CIMAV':
            ax2 .plot(np.arange(167), Q_prod[0:167],'.-',color = 'red',label="Disipación")
        else:
            ax2 .plot(np.arange(167), Q_prod[0:167],'.-',color = 'red',label="Desenfoque")
        ax2 .plot(np.arange(167), Q_prod_lim[0:167],'.-',color = 'blue',label="Producción solar")
        if type_integration=="SL_L_PS" or type_integration=='SL_S_FWS':
            ax2 .plot(np.arange(167), Q_charg[0:167],'.-',color = '#FFAE00',label="Carga")
            ax2 .plot(np.arange(167), Q_discharg[0:167],'.-',color = '#2EAD23',label="Descarga")
        ax2.set_ylabel('Producción y Demanda - kWh')
        ax2.set_ylim([0,np.max(Q_prod)*4.2])
        plt.legend(bbox_to_anchor=(1.00, 1), loc=1, borderaxespad=0.)
    #    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        plt.tight_layout()
    if lang=="eng": 
        fig.suptitle('Solar production first week January', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)
        
        ax1 .plot(np.arange(167), DNI[0:167],color='#CA6A16',linestyle='solid',label="Solar Radiation")
        ax1.set_xlabel('simulation time (hour of the year)')
        ax1.set_ylabel('Solar Radiation - W/m2')
        ax1.set_ylim([0,1200])
        plt.legend(loc='upper left', borderaxespad=0.,frameon=False)
        ax2 = ax1.twinx()
        plt.fill_between( np.arange(167), Demand[0:167], color="grey", alpha=0.2,label="Demand")          
        ax2 .plot(np.arange(167), Demand[0:167],'.-',color = '#362510',label="Demand")
        ax2 .plot(np.arange(167), Q_prod[0:167],'.-',color = 'red',label="Defocused")
        ax2 .plot(np.arange(167), Q_prod_lim[0:167],'.-',color = 'blue',label="Solar production")
        if type_integration=="SL_L_PS" or type_integration=='SL_S_FWS':
            ax2 .plot(np.arange(167), Q_charg[0:167],'.-',color = '#FFAE00',label="Charge")
            ax2 .plot(np.arange(167), Q_discharg[0:167],'.-',color = '#2EAD23',label="Discharge")
        ax2.set_ylabel('Production & Demand - kWh')
        ax2.set_ylim([0,np.max(Q_prod)*4.2])
        plt.legend(bbox_to_anchor=(1.00, 1), loc=1, borderaxespad=0.)
    #    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        plt.tight_layout()
    
#    output4=pd.DataFrame(DNI)
#    output4.columns=['DNI']
#    output5=pd.DataFrame(Demand)
#    output5.columns=['Demand']
#    output6=pd.DataFrame(Q_prod)
#    output6.columns=['Q_prod']
#    output_excel_Prod_wee_Jan=pd.concat([output1,output2,output3,output4,output5,output6], axis=1)
    
    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'produccion_solar1weekWinter.png', format='png', dpi=imageQlty)
 
def prodSummerPlot(sender,origin,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
        
    if lang=="spa":         
        fig.suptitle('Producción solar primera semana Junio', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)

        ax1 .plot((np.arange(3624,3624+167,1)), DNI[3624:3791],color='#CA6A16',linestyle='solid',label="Radiación solar")
        ax1.set_xlabel('simulación (hora del año)')
        ax1.set_ylabel('Radiación Solar - W/m2')
        ax1.set_ylim([0,1200])
        plt.legend(loc='upper left', borderaxespad=0.,frameon=False)
        ax2 = ax1.twinx()   
        ax2.fill_between( np.arange(3624,3624+167,1), Demand[3624:3791], color="grey", alpha=0.2,label="Demanda")
        ax2 .plot((np.arange(3624,3624+167,1)), Demand[3624:3791],'.-',color = '#362510',label="Demanda")
        if sender =='CIMAV':
            ax2 .plot((np.arange(3624,3624+167,1)), Q_prod[3624:3791],'.-',color = 'red',label="Disipación")
        else:
            ax2 .plot((np.arange(3624,3624+167,1)), Q_prod[3624:3791],'.-',color = 'red',label="Desenfoque")
        ax2 .plot((np.arange(3624,3624+167,1)), Q_prod_lim[3624:3791],'.-',color = 'blue',label="Producción solar")
        if type_integration=="SL_L_PS" or type_integration=='SL_S_FWS':
            ax2 .plot((np.arange(3624,3624+167,1)), Q_charg[3624:3791],'.-',color = '#FFAE00',label="Carga")
            ax2 .plot((np.arange(3624,3624+167,1)), Q_discharg[3624:3791],'.-',color = '#2EAD23',label="Descarga")
       
        ax2.set_ylabel('Producción y Demanda - kWh')
        ax2.set_ylim([0,np.max(Q_prod)*4.2])
        plt.legend(bbox_to_anchor=(1.00, 1), loc=1, borderaxespad=0.)
        plt.tight_layout()
    if lang=="eng":

        fig.suptitle('Solar production first week of June', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)
       
        ax1 .plot((np.arange(3624,3624+167,1)), DNI[3624:3791],color='#CA6A16',linestyle='solid',label="Solar Radiation")
        ax1.set_xlabel('simulation time (hour of the year)')
        ax1.set_ylabel('Solar Radiation - W/m2')
        ax1.set_ylim([0,1200])
        plt.legend(loc='upper left', borderaxespad=0.,frameon=False)
        ax2 = ax1.twinx()
        ax2.fill_between( np.arange(3624,3624+167,1), Demand[3624:3791], color="grey", alpha=0.2,label="Demand")          
        ax2 .plot((np.arange(3624,3624+167,1)), Demand[3624:3791],'.-',color = '#362510',label="Demand")
        ax2 .plot((np.arange(3624,3624+167,1)), Q_prod[3624:3791],'.-',color = 'red',label="Defocused")
        ax2 .plot((np.arange(3624,3624+167,1)), Q_prod_lim[3624:3791],'.-',color = 'blue',label="Solar Production")
        if type_integration=="SL_L_PS" or type_integration=='SL_S_FWS':
            ax2 .plot((np.arange(3624,3624+167,1)), Q_charg[3624:3791],'.-',color = '#FFAE00',label="Charge")
            ax2 .plot((np.arange(3624,3624+167,1)), Q_discharg[3624:3791],'.-',color = '#2EAD23',label="Discharge")
       
        ax2.set_ylabel('Production & Demand - kWh')
        ax2.set_ylim([0,np.max(Q_prod)*4.2])
        plt.legend(bbox_to_anchor=(1.00, 1), loc=1, borderaxespad=0.)
        plt.tight_layout()
    
#    output4=pd.DataFrame(DNI)
#    output4.columns=['DNI']
#    output5=pd.DataFrame(Demand)
#    output5.columns=['Demand']
#    output6=pd.DataFrame(Q_prod)
#    output6.columns=['Q_prod']
#    
#    output_excel_Prod_week_Jun=pd.concat([output1,output2,output3,output4,output5,output6], axis=1)
    
    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'produccion_solar1weekSummer.png', format='png', dpi=imageQlty)
 
    
def productionSolar(sender,origin,lang,step_sim,DNI,m_dot_min_kgs,steps_sim,Demand,Q_prod,Q_prod_lim,Q_charg,Q_discharg,type_integration,plotPath,imageQlty,**kwargs):
    fig = plt.figure(figsize=(14, 3.5))
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa": 
        fig.suptitle('Producción anual', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)  
        ax1 .plot(step_sim, DNI,'.r-',label="Radiación solar")
#        ax1 .axhline(y=m_dot_min_kgs,xmin=0,xmax=steps_sim,c="black",linewidth=0.5,zorder=0)
        ax1.set_xlabel('Simulación (hora del año)')
        ax1.set_ylabel('Solar radiation - W/m2',color='red')
        legend =plt.legend(bbox_to_anchor=(0.12, -.07), loc=1, borderaxespad=0.)
        ax2 = ax1.twinx()          
        ax2 .plot(step_sim, Demand,'.-',color = '#362510',label="Demanda")
        ax2 .plot(step_sim, Q_prod,'.-',color = '#831896',label="Producción solar")
        ax2 .plot(step_sim, Q_prod_lim,'.-',color = 'blue',label="Energía suministrada")
        if type_integration=="SL_L_PS" or type_integration=="SL_S_FWS":
            ax2 .plot(step_sim, Q_charg,'.-',color = '#FFAE00',label="Carga")
            ax2 .plot(step_sim, Q_discharg,'.-',color = '#2EAD23',label="Descarga")
        
        ax2.set_ylabel('Producción & Demanda - kWh')
        ax2.set_ylim([0,np.max(Q_prod)*2])
    
        plt.legend(bbox_to_anchor=(1.00, 1), loc=1, borderaxespad=0.)
        plt.tight_layout()
    
    if lang=="eng":
        fig.suptitle('Annual Production', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)  
        ax1 .plot(step_sim, DNI,'.r-',label="Solar Radiation")
#        ax1 .axhline(y=m_dot_min_kgs,xmin=0,xmax=steps_sim,c="black",linewidth=0.5,zorder=0)
        ax1.set_xlabel('simulation time (hour of the year)')
        ax1.set_ylabel('Solar radiation - W/m2',color='red')
        legend =plt.legend(bbox_to_anchor=(0.12, -.07), loc=1, borderaxespad=0.)
        ax2 = ax1.twinx()          
        ax2 .plot(step_sim, Demand,'.-',color = '#362510',label="Demand")
        ax2 .plot(step_sim, Q_prod,'.-',color = '#831896',label="Solar production")
        ax2 .plot(step_sim, Q_prod_lim,'.-',color = 'blue',label="Net production")
        if type_integration=="SL_L_PS" or type_integration=="SL_S_FWS":
            ax2 .plot(step_sim, Q_charg,'.-',color = '#FFAE00',label="Charge")
            ax2 .plot(step_sim, Q_discharg,'.-',color = '#2EAD23',label="Discharge")
        
        ax2.set_ylabel('Production & Demand - kWh')
        ax2.set_ylim([0,np.max(Q_prod)*2])
    
        plt.legend(bbox_to_anchor=(1.00, 1), loc=1, borderaxespad=0.)
        plt.tight_layout()
    
    #    output4=pd.DataFrame(DNI)
    #    output4.columns=['DNI']
    #    output5=pd.DataFrame(Demand)
    #    output5.columns=['Demand']
    #    output6=pd.DataFrame(Q_prod)
    #    output6.columns=['Q_prod']
    #
    #    output_excel_Prod_annual=pd.concat([output1,output2,output3,output4,output5,output6], axis=1)
    #    fig.savefig('/home/miguel/Desktop/Python_files/PLAT_VIRT/fresnel/Report/images/produccion_solar.png', format='png', dpi=imageQlty)
    
    if origin==-2 or origin == -3:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'produccion_solar.png', format='png', dpi=imageQlty)
       
    
def storageWinter(sender,origin,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty,**kwargs):
    fig = plt.figure(figsize=(14, 3.5))
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa":
        fig.suptitle('Almacenamiento primera semana Enero', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)  
        plt.fill_between( np.arange(167), Demand[0:167], color="grey", alpha=0.2)
        
        plt.bar(np.arange(167), np.array(Q_prod[0:167])-np.array(Q_charg[0:167]),color = 'blue',label="Producción Solar",align='center')
#        ax1 .plot(np.arange(167), Q_prod_lim[0:167],color = 'blue',label="Energía suministrada",linewidth=4)
#        ax1 .plot(np.arange(167), Q_useful[0:167],color = 'green',label="Energía útil",linewidth=2)
        
        ax1 .plot(np.arange(167), Demand[0:167],color = '#362510',label="Demanda",linewidth=2.0)
        if sender =='CIMAV':
            plt.bar(np.arange(167), Q_defocus[0:167],color = 'red',label="Disipación",bottom=np.array(Q_prod[0:167])-np.array(Q_defocus[0:167]),align='center')
        else:
            plt.bar(np.arange(167), Q_defocus[0:167],color = 'red',label="Desenfoque",bottom=np.array(Q_prod[0:167])-np.array(Q_defocus[0:167]),align='center')
           
        plt.bar(np.arange(167), Q_charg[0:167],color = '#FFAE00',label="Carga",bottom=np.array(Q_prod[0:167])-np.array(Q_charg[0:167])-np.array(Q_defocus[0:167]),align='center')
    
        plt.bar(np.arange(167), Q_discharg[0:167],color = '#2EAD23',label="Descarga",bottom=np.array(Q_prod[0:167]),align='center')
         
        ax1.set_ylabel('Producción & Demanda - kWh')
        ax1.set_ylim([0,np.max([np.max(Q_prod[0:167]),np.max(Demand[0:167])])*1.1])
        ax1.set_xlim([0,167])
        plt.legend(loc='upper left', borderaxespad=0.)
    
        ax2 = ax1.twinx()  
        if type_integration=="SL_L_S" or type_integration=="SL_L_S_PH":
            ax2 .plot(np.arange(167), np.array(T_alm_K[0:167])-273,'r',label="Temperatura",linewidth=2.0)
        ax2 .plot(np.arange(167), SOC[0:167],color='orange',linestyle=':',label="Carga del almacenamiento",linewidth=2.0)
        ax2.set_xlabel('simulación (hora del año)')
        ax2.set_ylabel('Estado de carga almacenamiento %',color = '#CA6A16')
        ax2.set_ylim([0,101])
        ax2.set_xlim([0,167])

    if lang=="eng":
        fig.suptitle('Storage during the first week of January', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)  
        plt.fill_between( np.arange(167), Demand[0:167], color="grey", alpha=0.2)
        plt.bar(np.arange(167), np.array(Q_prod[0:167])-np.array(Q_charg[0:167]),color = 'blue',label="Solar Production",align='center')
#        ax1 .plot(np.arange(167), Q_prod_lim[0:167],color = 'blue',label="Net production",linewidth=4)
#        ax1 .plot(np.arange(167), Q_useful[0:167],color = 'green',label="Useful energy",linewidth=2)
        
        ax1 .plot(np.arange(167), Demand[0:167],color = '#362510',label="Demand",linewidth=2.0)
        plt.bar(np.arange(167), Q_defocus[0:167],color = 'red',label="Defocused",bottom=np.array(Q_prod[0:167])-np.array(Q_defocus[0:167]),align='center')
           
        plt.bar(np.arange(167), Q_charg[0:167],color = '#FFAE00',label="Charge",bottom=np.array(Q_prod[0:167])-np.array(Q_charg[0:167])-np.array(Q_defocus[0:167]),align='center')
    
        plt.bar(np.arange(167), Q_discharg[0:167],color = '#2EAD23',label="Discharge",bottom=np.array(Q_prod[0:167]),align='center')
         
        ax1.set_ylabel('Production & Demand - kWh')
        ax1.set_ylim([0,np.max([np.max(Q_prod[0:167]),np.max(Demand[0:167])])*1.1])
        ax1.set_xlim([0,167])

        plt.legend(loc='upper left', borderaxespad=0.)
        
        ax2 = ax1.twinx()
        if type_integration=="SL_L_S" or type_integration=="SL_L_S_PH":
            ax2 .plot(np.arange(167), np.array(T_alm_K[0:167])-273,'r',label="Temperature",linewidth=2.0)
      
        ax2 .plot(np.arange(167), SOC[0:167],color='orange',linestyle=':',label="Storage's state of charge",linewidth=2.0)
        ax2.set_xlabel('simulation time (hour of the year)')
        ax2.set_ylabel("Storage's state of charge %",color = '#CA6A16')
        ax2.set_ylim([0,101])
        ax2.set_xlim([0,167])

    
    plt.tight_layout()
    
    
    if origin==-2 or origin == -3:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'almacenamiento_Enero.png', format='png', dpi=imageQlty)

def storageSummer(sender,origin,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty,**kwargs):
    fig = plt.figure(figsize=(14, 3.5))
    #np.array(in list) is because Django need it since Q_prod, Q_prod_lim,.. are passed as lists
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa":
        fig.suptitle('Almacenamiento primera semana Junio', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)  
    
        plt.fill_between( np.arange(3624,3624+167,1), Demand[3624:3791], color="grey", alpha=0.2)

        plt.bar((np.arange(3624,3624+167,1)), np.array(Q_prod[3624:3791])-np.array(Q_charg[3624:3791]),color = 'blue',label="Producción Solar",align='center')
        #ax1 .plot((np.arange(3624,3624+167,1)), Q_prod_lim[3624:3791],color = 'blue',label="Energía suministrada",linewidth=4)
        #ax1 .plot((np.arange(3624,3624+167,1)), Q_useful[3624:3791],color = 'green',label="Energía útil",linewidth=2)
        
        ax1 .plot((np.arange(3624,3624+167,1)), Demand[3624:3791],color = '#362510',label="Demanda",linewidth=2.0)
        if sender =='CIMAV':
            plt.bar((np.arange(3624,3624+167,1)), Q_defocus[3624:3791],color = 'red',label="Disipación",bottom=np.array(Q_prod[3624:3791])-np.array(Q_defocus[3624:3791]),align='center')
        else:
            plt.bar((np.arange(3624,3624+167,1)), Q_defocus[3624:3791],color = 'red',label="Desenfoque",bottom=np.array(Q_prod[3624:3791])-np.array(Q_defocus[3624:3791]),align='center')
           
        plt.bar((np.arange(3624,3624+167,1)), Q_charg[3624:3791],color = '#FFAE00',label="Carga",bottom=np.array(Q_prod[3624:3791])-np.array(Q_charg[3624:3791])-np.array(Q_defocus[3624:3791]),align='center')
    
        plt.bar((np.arange(3624,3624+167,1)), Q_discharg[3624:3791],color = '#2EAD23',label="Descarga",bottom=Q_prod[3624:3791],align='center')
         
        ax1.set_ylabel('Producción & Demanda - kWh')
        ax1.set_ylim([0,np.max([np.max(Q_prod[3624:3791]),np.max(Demand[3624:3791])])*1.1])
        ax1.set_xlim([3624,3624+167])
        ax1.legend(loc='upper left', borderaxespad=0.).set_zorder(99)
        
        
        
        ax2 = ax1.twinx()
        if type_integration=="SL_L_S" or type_integration=="SL_L_S_PH":
             ax2 .plot((np.arange(3624,3624+167,1)), np.array(T_alm_K[3624:3791])-273,'r',label="Carga del almacenamiento",linewidth=2.0,zorder=11)
        ax2 .plot((np.arange(3624,3624+167,1)), SOC[3624:3791],color='orange',linestyle=':',label="Carga del almacenamiento",linewidth=2.0,zorder=11)
        ax2.set_xlabel('simulación (hora del año)')
        ax2.set_ylabel('Estado de carga almacenamiento %',color = '#CA6A16')
        ax2.set_ylim([0,101])
        ax2.set_xlim([3624,3624+167])
        
        
    if lang=="eng":
        fig.suptitle('Storage during the first week of June', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)  
        plt.fill_between( np.arange(3624,3624+167,1), Demand[3624:3791], color="grey", alpha=0.2)
        plt.bar((np.arange(3624,3624+167,1)), np.array(Q_prod[3624:3791])-np.array(Q_charg[3624:3791]),color = 'blue',label="Solar Production",align='center')
        #ax1 .plot((np.arange(3624,3624+167,1)), Q_prod_lim[3624:3791],color = 'blue',label="Net Production",linewidth=4)
        #ax1 .plot((np.arange(3624,3624+167,1)), Q_useful[3624:3791],color = 'green',label="Useful energy",linewidth=2)
        
        ax1 .plot((np.arange(3624,3624+167,1)), Demand[3624:3791],color = '#362510',label="Demand",linewidth=2.0)
        plt.bar((np.arange(3624,3624+167,1)), Q_defocus[3624:3791],color = 'red',label="Defocused",bottom=np.array(Q_prod[3624:3791])-np.array(Q_defocus[3624:3791]),align='center')
           
        plt.bar((np.arange(3624,3624+167,1)), Q_charg[3624:3791],color = '#FFAE00',label="Charge",bottom=np.array(Q_prod[3624:3791])-np.array(Q_charg[3624:3791])-np.array(Q_defocus[3624:3791]),align='center')
    
        plt.bar((np.arange(3624,3624+167,1)), Q_discharg[3624:3791],color = '#2EAD23',label="Discharge",bottom=Q_prod[3624:3791],align='center')
         
        ax1.set_ylabel('Production & Demand - kWh')
        ax1.set_ylim([0,np.max([np.max(Q_prod[3624:3791]),np.max(Demand[3624:3791])])*1.1])
        ax1.set_xlim([3624,3624+167])
    
        plt.legend(loc='upper left', borderaxespad=0.)
        
        ax2 = ax1.twinx()  
        ax2 .plot((np.arange(3624,3624+167,1)), SOC[3624:3791],color='orange',linestyle=':',label="Storage's state of charge %",linewidth=2.0)
        ax2.set_xlabel('simulation time (hour of the year)')
        ax2.set_ylabel("Storage's state of charge %",color = '#CA6A16')
        ax2.set_ylim([0,101])
        ax2.set_xlim([3624,3624+167])
    
    plt.tight_layout()
    
    
    if origin==-2 or origin == -3:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'almacenamiento_Junio.png', format='png', dpi=imageQlty)

def storageNonAnnual(sender,origin,SOC,Q_useful,Q_prod,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty,**kwargs):
    fig = plt.figure(figsize=(14, 3.5))
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    fig.suptitle('Almacenamiento', fontsize=14, fontweight='bold',y=1)
    ax1 = fig.add_subplot(111)  

    plt.bar(step_sim, Q_prod-Q_charg,color = '#1F85DE',label="Producción Solar",align='center')
    ax1 .plot(step_sim, Q_prod_lim,color = 'blue',label="Energía suministrada",linewidth=4)
    ax1 .plot(step_sim, Q_useful,color = 'green',label="Energía útil",linewidth=2)
    ax1 .plot(step_sim, Demand,color = '#362510',label="Demanda")
    if sender =='CIMAV':
        plt.bar(step_sim, Q_defocus,color = 'red',label="Disipación",bottom=Q_prod-Q_defocus,align='center')
    else:
        plt.bar(step_sim, Q_defocus,color = 'red',label="Desenfoque",bottom=Q_prod-Q_defocus,align='center')
       
    plt.bar(step_sim, Q_charg,color = '#FFAE00',label="Carga",bottom=Q_prod-Q_charg-Q_defocus,align='center')

    plt.bar(step_sim, Q_discharg,color = '#2EAD23',label="Descarga",bottom=Q_prod,align='center')
     
    ax1.set_ylabel('Producción & Demanda - kWh')
    ax1.set_ylim([0,max(np.max(Q_prod),np.max(Demand))*1.2])
    ax1.set_xlim([0,steps_sim])

    plt.legend(loc='upper left', borderaxespad=0.)
    
    ax2 = ax1.twinx()  
    ax2 .plot(step_sim, SOC,'.r-',label="Carga del almacenamiento")
    ax2.set_xlabel('simulación (hora del año)')
    ax2.set_ylabel('Estado de carga almacenamiento %',color = '#CA6A16')
    ax2.set_ylim([0,101])
    ax2.set_xlim([0,steps_sim])
   
    plt.tight_layout()
    
    
    if origin==-2 or origin == -3:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'almacenamiento_Anual.png', format='png', dpi=imageQlty)
        
def storageNonAnnualSL_S_PDR(sender,origin,SOC,Q_useful,Q_prod_steam,Q_prod,Q_drum,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty,**kwargs):
    fig = plt.figure(figsize=(14, 3.5))
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    fig.suptitle('Almacenamiento', fontsize=14, fontweight='bold',y=1)
    ax1 = fig.add_subplot(111)  

    plt.bar(step_sim, Q_prod-Q_charg,color = '#1F85DE',label="Producción solar en el campo",align='center')
    plt.bar(step_sim, Q_prod_steam,color = '#7EE4E9',label="Producción de Vapor",align='center')
    ax1 .plot(step_sim, Q_prod_lim,color = 'blue',label="Energía suministrada",linewidth=4)
    ax1 .plot(step_sim, Q_useful,color = 'green',label="Energía útil",linewidth=2)
    ax1 .plot(step_sim, Demand,color = '#362510',label="Demanda")

    plt.bar(step_sim, Q_drum,color = '#FFAE00',label="Energía al drum",bottom=Q_prod_steam,align='center')
    plt.bar(step_sim, Q_defocus,color = 'red',label="Desenfoque",bottom=Q_prod_steam+Q_drum,align='center')

    ax1.set_ylabel('Producción & Demanda - kWh')
    ax1.set_ylim([0,max(np.max(Q_prod_steam+Q_drum+Q_defocus),np.max(Demand))*1.2])
    ax1.set_xlim([0,steps_sim])

    plt.legend(loc='upper left', borderaxespad=0.)

    ax2 = ax1.twinx()  
    ax2 .plot(step_sim, SOC,'.r-',label="Carga del almacenamiento")
    ax2.set_xlabel('simulación (hora del año)')
    ax2.set_ylabel('Estado de carga almacenamiento %',color = '#CA6A16')
    ax2.set_ylim([0,101])
    ax2.set_xlim([0,steps_sim])

    plt.tight_layout()


    if origin==-2 or origin == -3:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'almacenamiento_Anual.png', format='png', dpi=imageQlty)

def storageNonAnnualSL_S_PDR(sender,origin,SOC,Q_useful,Q_prod_steam,Q_prod,Q_drum,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty,**kwargs):
    fig = plt.figure(figsize=(14, 3.5))
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    fig.suptitle('Almacenamiento', fontsize=14, fontweight='bold',y=1)
    ax1 = fig.add_subplot(111)  

    plt.bar(step_sim, Q_prod-Q_charg,color = '#1F85DE',label="Producción solar en el campo",align='center')
    plt.bar(step_sim, Q_prod_steam,color = '#7EE4E9',label="Producción de Vapor",align='center')
    ax1 .plot(step_sim, Q_prod_lim,color = 'blue',label="Energía suministrada",linewidth=4)
    ax1 .plot(step_sim, Q_useful,color = 'green',label="Energía útil",linewidth=2)
    ax1 .plot(step_sim, Demand,color = '#362510',label="Demanda")
    
    plt.bar(step_sim, Q_drum,color = '#FFAE00',label="Energía al drum",bottom=Q_prod_steam,align='center')
    plt.bar(step_sim, Q_defocus,color = 'red',label="Desenfoque",bottom=Q_prod_steam+Q_drum,align='center')
       
    ax1.set_ylabel('Producción & Demanda - kWh')
    ax1.set_ylim([0,max(np.max(Q_prod_steam+Q_drum+Q_defocus),np.max(Demand))*1.2])
    ax1.set_xlim([0,steps_sim])

    plt.legend(loc='upper left', borderaxespad=0.)
    
    ax2 = ax1.twinx()  
    ax2 .plot(step_sim, SOC,'.r-',label="Carga del almacenamiento")
    ax2.set_xlabel('simulación (hora del año)')
    ax2.set_ylabel('Estado de carga almacenamiento %',color = '#CA6A16')
    ax2.set_ylim([0,101])
    ax2.set_xlim([0,steps_sim])
   
    plt.tight_layout()
    
    
    if origin==-2 or origin == -3:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'almacenamiento_Anual.png', format='png', dpi=imageQlty)
    


def financePlot(sender,origin,lang,n_years_sim,Acum_FCF,FCF,m_dot_min_kgs,steps_sim,AmortYear,Selling_price,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa":
        fig.suptitle('Estudio financiero', fontsize=14, fontweight='bold')
        ax1 = fig.add_subplot(111)  
        ax1 .plot(np.arange(n_years_sim), Acum_FCF,'.k-',label="Cash Flow acumulado")
        ax1 .plot(np.arange(n_years_sim), FCF,'.b-',label="Cash Flow")
        ax1 .axhline(y=m_dot_min_kgs,xmin=0,xmax=steps_sim,c="black",linewidth=0.5,zorder=0)
        ax1.set_xlabel('años')
        if origin == -3:
            ax1.set_ylabel('$')
        else:
            ax1.set_ylabel('€')
        plt.legend(bbox_to_anchor=(1.15, .5), loc=2, borderaxespad=0.)
        plt.text(int(AmortYear),-Selling_price, "Año de retorno= "+str(int(AmortYear)))
    if lang=="eng":    
        fig.suptitle('Financial study', fontsize=14, fontweight='bold')
        ax1 = fig.add_subplot(111)  
        ax1 .plot(np.arange(n_years_sim), Acum_FCF,'.k-',label="Accumulated Free Cash Flows")
        ax1 .plot(np.arange(n_years_sim), FCF,'.b-',label="Free Cash Flows")
        ax1 .axhline(y=m_dot_min_kgs,xmin=0,xmax=steps_sim,c="black",linewidth=0.5,zorder=0)
        ax1.set_xlabel('years')
        if origin == -3:
            ax1.set_ylabel('$')
        else:
            ax1.set_ylabel('€')
        plt.legend(bbox_to_anchor=(1.15, .5), loc=2, borderaxespad=0.)
        plt.text(int(AmortYear),-Selling_price, "Payback period= "+str(int(AmortYear)))    
    
    
#    plt.text(1,Acum_FCF[n_years_sim-1]*.55,"IRR: "+ str(round(IRR,2))+"%", bbox={'boxstyle':'square', 'color':'#A0D8EB'})
#    plt.text(1,Acum_FCF[n_years_sim-1]*.35,"Solar_fraction: "+ str(round(solar_fraction_lim,1))+"%", bbox={'boxstyle':'square', 'color':'#A0D8EB'})
#    plt.text(1,Acum_FCF[n_years_sim-1]*.85,"Energy_bill: "+ str(round(energy_bill))+"€", bbox={'boxstyle':'square', 'color':'#A0D8EB'})
#    plt.text(1,Acum_FCF[n_years_sim-1]*.7,"Savings: "+ str(round(Solar_savings_lim))+"€", bbox={'boxstyle':'square', 'color':'#A0D8EB'})
#    plt.text(1,Acum_FCF[n_years_sim-1]*.45,"Investment: "+ str(round(Selling_price))+"€", bbox={'boxstyle':'square', 'color':'#A0D8EB'})
#    plt.text(1,Acum_FCF[n_years_sim-1],"Solar Irradiation: "+ str(round(DNI_anual_irradiation,1))+"kWh/m2", bbox={'boxstyle':'square', 'color':'#A0D8EB'})
#   #        ax2 = ax1.twinx()          
#        ax2 .plot(step_sim, Demand,'.-',color = 'red',label="Demand")
#        ax2 .plot(step_sim, Q_prod,'.-',color = '#617824',label="Q_prod")
#        ax2 .plot(step_sim, Q_prod_lim,'.-',color = 'blue',label="Q_prod_lim")
#        ax2.set_ylabel('QProd vs DEmand - kWh')
        
    plt.legend(bbox_to_anchor=(0, 1), loc=2, borderaxespad=0.)
    
    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'finance.png', format='png', dpi=imageQlty)
        

def arraysMonth(Q_prod,Q_prod_lim,DNI,Demand,**kwargs):
 #Para resumen mensual      
    Ene_prod=np.zeros(8760)
    Feb_prod=np.zeros(8760)
    Mar_prod=np.zeros(8760)
    Abr_prod=np.zeros(8760)
    May_prod=np.zeros(8760)
    Jun_prod=np.zeros(8760)
    Jul_prod=np.zeros(8760)
    Ago_prod=np.zeros(8760)
    Sep_prod=np.zeros(8760)
    Oct_prod=np.zeros(8760)
    Nov_prod=np.zeros(8760)
    Dic_prod=np.zeros(8760)
    Ene_prod_lim=np.zeros(8760)
    Feb_prod_lim=np.zeros(8760)
    Mar_prod_lim=np.zeros(8760)
    Abr_prod_lim=np.zeros(8760)
    May_prod_lim=np.zeros(8760)
    Jun_prod_lim=np.zeros(8760)
    Jul_prod_lim=np.zeros(8760)
    Ago_prod_lim=np.zeros(8760)
    Sep_prod_lim=np.zeros(8760)
    Oct_prod_lim=np.zeros(8760)
    Nov_prod_lim=np.zeros(8760)
    Dic_prod_lim=np.zeros(8760)
    Ene_DNI=np.zeros(8760)
    Feb_DNI=np.zeros(8760)
    Mar_DNI=np.zeros(8760)
    Abr_DNI=np.zeros(8760)
    May_DNI=np.zeros(8760)
    Jun_DNI=np.zeros(8760)
    Jul_DNI=np.zeros(8760)
    Ago_DNI=np.zeros(8760)
    Sep_DNI=np.zeros(8760)
    Oct_DNI=np.zeros(8760)
    Nov_DNI=np.zeros(8760)
    Dic_DNI=np.zeros(8760)
    Ene_demd=np.zeros(8760)
    Feb_demd=np.zeros(8760)
    Mar_demd=np.zeros(8760)
    Abr_demd=np.zeros(8760)
    May_demd=np.zeros(8760)
    Jun_demd=np.zeros(8760)
    Jul_demd=np.zeros(8760)
    Ago_demd=np.zeros(8760)
    Sep_demd=np.zeros(8760)
    Oct_demd=np.zeros(8760)
    Nov_demd=np.zeros(8760)
    Dic_demd=np.zeros(8760)

    for i in range(0,8759):
        if (i<=744-1):
            Ene_prod[i]=Q_prod[i]
            Ene_prod_lim[i]=Q_prod_lim[i]
            Ene_DNI[i]=DNI[i]
            Ene_demd[i]=Demand[i]
        if (i>744-1) and (i<=1416-1):
            Feb_prod[i]=Q_prod[i]
            Feb_prod_lim[i]=Q_prod_lim[i]
            Feb_DNI[i]=DNI[i]
            Feb_demd[i]=Demand[i]
        if (i>1416-1) and (i<=2160-1):
            Mar_prod[i]=Q_prod[i]
            Mar_prod_lim[i]=Q_prod_lim[i]
            Mar_DNI[i]=DNI[i]
            Mar_demd[i]=Demand[i]
        if (i>2160-1) and (i<=2880-1):
            Abr_prod[i]=Q_prod[i]
            Abr_prod_lim[i]=Q_prod_lim[i]
            Abr_DNI[i]=DNI[i]
            Abr_demd[i]=Demand[i]
        if (i>2880-1) and (i<=3624-1):
            May_prod[i]=Q_prod[i]
            May_prod_lim[i]=Q_prod_lim[i]
            May_DNI[i]=DNI[i] 
            May_demd[i]=Demand[i]
        if (i>3624-1) and (i<=4344-1):
            Jun_prod[i]=Q_prod[i]
            Jun_prod_lim[i]=Q_prod_lim[i]
            Jun_DNI[i]=DNI[i] 
            Jun_demd[i]=Demand[i]
        if (i>4344-1) and (i<=5088-1):
            Jul_prod[i]=Q_prod[i]
            Jul_prod_lim[i]=Q_prod_lim[i]
            Jul_DNI[i]=DNI[i]
            Jul_demd[i]=Demand[i]
        if (i>5088-1) and (i<=5832-1):
            Ago_prod[i]=Q_prod[i]
            Ago_prod_lim[i]=Q_prod_lim[i]
            Ago_DNI[i]=DNI[i] 
            Ago_demd[i]=Demand[i]
        if (i>5832-1) and (i<=6552-1):
            Sep_prod[i]=Q_prod[i]
            Sep_prod_lim[i]=Q_prod_lim[i]
            Sep_DNI[i]=DNI[i]
            Sep_demd[i]=Demand[i]
        if (i>6552-1) and (i<=7296-1):
            Oct_prod[i]=Q_prod[i]
            Oct_prod_lim[i]=Q_prod_lim[i]
            Oct_DNI[i]=DNI[i]
            Oct_demd[i]=Demand[i]
        if (i>7296-1) and (i<=8016-1):
            Nov_prod[i]=Q_prod[i]
            Nov_prod_lim[i]=Q_prod_lim[i]
            Nov_DNI[i]=DNI[i]
            Nov_demd[i]=Demand[i]
        if (i>8016-1):
            Dic_prod[i]=Q_prod[i]
            Dic_prod_lim[i]=Q_prod_lim[i]
            Dic_DNI[i]=DNI[i]
            Dic_demd[i]=Demand[i]
    array_de_meses=[np.sum(Ene_prod),np.sum(Feb_prod),np.sum(Mar_prod),np.sum(Abr_prod),np.sum(May_prod),np.sum(Jun_prod),np.sum(Jul_prod),np.sum(Ago_prod),np.sum(Sep_prod),np.sum(Oct_prod),np.sum(Nov_prod),np.sum(Dic_prod)]
    array_de_meses_lim=[np.sum(Ene_prod_lim),np.sum(Feb_prod_lim),np.sum(Mar_prod_lim),np.sum(Abr_prod_lim),np.sum(May_prod_lim),np.sum(Jun_prod_lim),np.sum(Jul_prod_lim),np.sum(Ago_prod_lim),np.sum(Sep_prod_lim),np.sum(Oct_prod_lim),np.sum(Nov_prod_lim),np.sum(Dic_prod_lim)]   
    array_de_DNI=[np.sum(Ene_DNI),np.sum(Feb_DNI),np.sum(Mar_DNI),np.sum(Abr_DNI),np.sum(May_DNI),np.sum(Jun_DNI),np.sum(Jul_DNI),np.sum(Ago_DNI),np.sum(Sep_DNI),np.sum(Oct_DNI),np.sum(Nov_DNI),np.sum(Dic_DNI)]
    array_de_demd=[np.sum(Ene_demd),np.sum(Feb_demd),np.sum(Mar_demd),np.sum(Abr_demd),np.sum(May_demd),np.sum(Jun_demd),np.sum(Jul_demd),np.sum(Ago_demd),np.sum(Sep_demd),np.sum(Oct_demd),np.sum(Nov_demd),np.sum(Dic_demd)]
    array_de_fraction=np.zeros(12)

    return array_de_meses,array_de_meses_lim,array_de_DNI,array_de_demd,array_de_fraction

def prodMonths(sender,origin,Q_prod,Q_prod_lim,DNI,Demand,lang,plotPath,imageQlty,**kwargs):
    array_de_meses,array_de_meses_lim,array_de_DNI,array_de_demd,array_de_fraction=arraysMonth(Q_prod,Q_prod_lim,DNI,Demand)
    for m in range(0,12):
        if array_de_demd[m]==0:
            array_de_fraction[m]=0
        else:
            array_de_fraction[m]=100*array_de_meses[m]/array_de_demd[m]
  
    output1=pd.DataFrame(array_de_meses)
    output1.columns=['Prod.mensual']
    output2=pd.DataFrame(array_de_DNI)/1000
    output2.columns=['DNI']
    output3=pd.DataFrame(array_de_demd)
    output3.columns=['Demanda']
    output4=pd.DataFrame(array_de_meses_lim)
    output4.columns=['Prod.mensual_lim']
    output_excel=pd.concat([output1,output2,output3,output4], axis=1)
    

    meses=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dec"]
    meses_index=np.arange(0,12)
    fig,ax = plt.subplots()
    
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa":
        meses=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dec"]
        fig.suptitle('Producción & Demanda energía de proceso', fontsize=14, fontweight='bold')
        
        ax.set_ylabel('Producción y Demanda en kWh',color = 'black')
        ax.bar(meses_index, output3['Demanda'], width=0.8, color='#362510',label="Demanda")
        if sender =='CIMAV':
            ax.bar(meses_index, output1['Prod.mensual'], width=0.8, color='red',label="Disipada")
        else:
            ax.bar(meses_index, output1['Prod.mensual'], width=0.8, color='red',label="Desenfocada")
        ax.bar(meses_index, output4['Prod.mensual_lim'], width=0.8, color='blue',label="Producción solar")
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.05), ncol=3)     
        ax2 = ax.twinx()          
        ax2 .plot([0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5], output2['DNI'],'-',color = '#CA6A16',label="Radiación solar",linewidth=2.0)
        ax2.set_ylabel('Radiacion solar [kWh/m2]',color = '#CA6A16')    
        ax.set_xticks(meses_index+.4)  # set the x ticks to be at the middle of each bar since the width of each bar is 0.8
        ax.set_xticklabels(meses)  #replace the name of the x ticks with your Groups name 
        plt.legend(loc='upper right', borderaxespad=0.,frameon=True)

    if lang=="eng":
        meses=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        fig.suptitle('Production & Demand process energy', fontsize=14, fontweight='bold')
        ax.set_ylabel('Production & Demand kWh',color = 'black')
        ax.bar(meses_index, output3['Demanda'], width=0.8, color='#362510',label="Demand")
        ax.bar(meses_index, output1['Prod.mensual'], width=0.8, color='red',label="Defocused")
        ax.bar(meses_index, output4['Prod.mensual_lim'], width=0.8, color='blue',label="Solar production")
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.05), ncol=3)         
        ax2 = ax.twinx()          
        ax2 .plot([0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5], output2['DNI'],'-',color = '#CA6A16',label="Solar Radiation",linewidth=2.0)
        ax2.set_ylabel('Solar Radiation [kWh/m2]',color = '#CA6A16')    
        ax.set_xticks(meses_index+.4)  # set the x ticks to be at the middle of each bar since the width of each bar is 0.8
        ax.set_xticklabels(meses)  #replace the name of the x ticks with your Groups name  
        plt.legend(loc='upper right', borderaxespad=0.,frameon=True)        
      
    
    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'prodMonths.png', format='png', dpi=imageQlty)  
    if origin==0:
        plt.show()
        return output_excel

def arrays_Savings_Month(Q_prod_lim,Demand,Fuel_price,Boiler_eff,**kwargs):
 #Para resumen mensual      

    Ene_sav_lim=np.zeros(8760)
    Feb_sav_lim=np.zeros(8760)
    Mar_sav_lim=np.zeros(8760)
    Abr_sav_lim=np.zeros(8760)
    May_sav_lim=np.zeros(8760)
    Jun_sav_lim=np.zeros(8760)
    Jul_sav_lim=np.zeros(8760)
    Ago_sav_lim=np.zeros(8760)
    Sep_sav_lim=np.zeros(8760)
    Oct_sav_lim=np.zeros(8760)
    Nov_sav_lim=np.zeros(8760)
    Dic_sav_lim=np.zeros(8760)
    Ene_demd=np.zeros(8760)
    Feb_demd=np.zeros(8760)
    Mar_demd=np.zeros(8760)
    Abr_demd=np.zeros(8760)
    May_demd=np.zeros(8760)
    Jun_demd=np.zeros(8760)
    Jul_demd=np.zeros(8760)
    Ago_demd=np.zeros(8760)
    Sep_demd=np.zeros(8760)
    Oct_demd=np.zeros(8760)
    Nov_demd=np.zeros(8760)
    Dic_demd=np.zeros(8760)
    Ene_frac=np.zeros(8760)
    Feb_frac=np.zeros(8760)
    Mar_frac=np.zeros(8760)
    Abr_frac=np.zeros(8760)
    May_frac=np.zeros(8760)
    Jun_frac=np.zeros(8760)
    Jul_frac=np.zeros(8760)
    Ago_frac=np.zeros(8760)
    Sep_frac=np.zeros(8760)
    Oct_frac=np.zeros(8760)
    Nov_frac=np.zeros(8760)
    Dic_frac=np.zeros(8760)

    for i in range(0,8759):
        if (i<=744-1):
            Ene_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Ene_demd[i]=Fuel_price*Demand[i]
            if Ene_demd[i] == 0:
                Ene_frac[i] = 0
            else:
                Ene_frac[i]=Ene_sav_lim[i]/Ene_demd[i]
        if (i>744-1) and (i<=1416-1):
            Feb_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Feb_demd[i]=Fuel_price*Demand[i]
            if Feb_demd[i] == 0:
                Feb_frac[i] = 0
            else:
                Feb_frac[i]=Feb_sav_lim[i]/Feb_demd[i]
        if (i>1416-1) and (i<=2160-1):
            Mar_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Mar_demd[i]=Fuel_price*Demand[i]
            if Mar_demd[i] == 0:
                Mar_frac[i] = 0
            else:
                Mar_frac[i]=Mar_sav_lim[i]/Mar_demd[i]
        if (i>2160-1) and (i<=2880-1):
            Abr_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Abr_demd[i]=Fuel_price*Demand[i]
            if Abr_demd[i] == 0:
                Abr_frac[i] = 0
            else:
                Abr_frac[i]=Abr_sav_lim[i]/Abr_demd[i]
        if (i>2880-1) and (i<=3624-1):
            May_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            May_demd[i]=Fuel_price*Demand[i]
            if May_demd[i] == 0:
                May_frac[i] = 0
            else:
                May_frac[i]=May_sav_lim[i]/May_demd[i]
        if (i>3624-1) and (i<=4344-1):
            Jun_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Jun_demd[i]=Fuel_price*Demand[i]
            if Jun_demd[i] == 0:
                Jun_frac[i] = 0
            else:
                Jun_frac[i]=Jun_sav_lim[i]/Jun_demd[i]
        if (i>4344-1) and (i<=5088-1):
            Jul_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Jul_demd[i]=Fuel_price*Demand[i]
            if Jul_demd[i] == 0:
                Jul_frac[i] = 0
            else:
                Jul_frac[i]=Jul_sav_lim[i]/Jul_demd[i]
        if (i>5088-1) and (i<=5832-1):
            Ago_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Ago_demd[i]=Fuel_price*Demand[i]
            if Ago_demd[i] == 0:
                Ago_frac[i] = 0
            else:
                Ago_frac[i]=Ago_sav_lim[i]/Ago_demd[i]
        if (i>5832-1) and (i<=6552-1):
            Sep_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Sep_demd[i]=Fuel_price*Demand[i]
            if Sep_demd[i] == 0:
                Sep_frac[i] = 0
            else:
                Sep_frac[i]=Sep_sav_lim[i]/Sep_demd[i]
        if (i>6552-1) and (i<=7296-1):
            Oct_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Oct_demd[i]=Fuel_price*Demand[i]
            if Oct_demd[i] == 0:
                Oct_frac[i] = 0
            else:
                Oct_frac[i]=Oct_sav_lim[i]/Oct_demd[i]
        if (i>7296-1) and (i<=8016-1):
            Nov_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Nov_demd[i]=Fuel_price*Demand[i]
            if Nov_demd[i] == 0:
                Nov_frac[i] = 0
            else:
                Nov_frac[i]=Nov_sav_lim[i]/Nov_demd[i]
        if (i>8016-1):
            Dic_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Dic_demd[i]=Fuel_price*Demand[i]
            if Dic_demd[i] == 0:
                Dic_frac[i] = 0
            else:
                Dic_frac[i]=Dic_sav_lim[i]/Dic_demd[i]

    array_de_meses_lim=[np.sum(Ene_sav_lim),np.sum(Feb_sav_lim),np.sum(Mar_sav_lim),np.sum(Abr_sav_lim),np.sum(May_sav_lim),np.sum(Jun_sav_lim),np.sum(Jul_sav_lim),np.sum(Ago_sav_lim),np.sum(Sep_sav_lim),np.sum(Oct_sav_lim),np.sum(Nov_sav_lim),np.sum(Dic_sav_lim)]   
    array_de_demd=[np.sum(Ene_demd),np.sum(Feb_demd),np.sum(Mar_demd),np.sum(Abr_demd),np.sum(May_demd),np.sum(Jun_demd),np.sum(Jul_demd),np.sum(Ago_demd),np.sum(Sep_demd),np.sum(Oct_demd),np.sum(Nov_demd),np.sum(Dic_demd)]
    array_de_fraction=[np.sum(Ene_frac),np.sum(Feb_frac),np.sum(Mar_frac),np.sum(Abr_frac),np.sum(May_frac),np.sum(Jun_frac),np.sum(Jul_frac),np.sum(Ago_frac),np.sum(Sep_frac),np.sum(Oct_frac),np.sum(Nov_frac),np.sum(Dic_frac)]   

    return array_de_meses_lim,array_de_demd,array_de_fraction

    
def savingsMonths(sender,origin,Q_prod_lim,Demand,Fuel_price,Boiler_eff,lang,plotPath,imageQlty,**kwargs):
    array_de_meses_lim,array_de_demd,array_de_fraction=arrays_Savings_Month(Q_prod_lim,Demand,Fuel_price,Boiler_eff)
  
    output2=pd.DataFrame(array_de_fraction)
    output2.columns=['Fraccion']
    output3=pd.DataFrame(array_de_demd)
    output3.columns=['Demanda']
    output4=pd.DataFrame(array_de_meses_lim)
    output4.columns=['Ahorro mensual']
    output_excel=pd.concat([output3,output4], axis=1)
    

    meses=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    meses_index=np.arange(0,12)
    fig = plt.figure(figsize=(10, 5))
#    fig = plt.figure()
#    fig,ax = plt.subplots()

    ax = fig.add_subplot(111) 
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa":
        meses=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dec"]
        fig.suptitle('Ahorro solar', fontsize=14, fontweight='bold')
        if origin == -3:
            ax.set_ylabel('Ahorro solar / Factura actual $') 
        else:
            ax.set_ylabel('Ahorro solar / Factura actual €') 
        ax.bar(meses_index, output3['Demanda'], width=0.8, color='#362510',label="Factura mensual")
        ax.bar(meses_index, output4['Ahorro mensual'], width=0.8, color='blue',label="Ahorro solar")
        ax.set_xticks(meses_index) 
        ax.set_xticklabels(meses)  #replace the name of the x ticks with your Groups name 
        L=plt.legend(loc=9, bbox_to_anchor=(0.5, -0.05), ncol=3) 

        
    if lang=="eng":
        meses=["Jan","Feb","Mar","Abr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        fig.suptitle('Solar savings', fontsize=14, fontweight='bold')
        if origin == -3:
            ax.set_ylabel('Solar savings / Monthly energy cost $') 
        else:
            ax.set_ylabel('Solar savings / Monthly energy cost €') 
        ax.bar(meses_index, output3['Demanda'], width=0.8, color='#362510',label="Monthly energy cost")
        ax.bar(meses_index, output4['Ahorro mensual'], width=0.8, color='blue',label="Solar savings")
        ax.set_xticks(meses_index)  
        ax.set_xticklabels(meses)  #replace the name of the x ticks with your Groups name 
        L=plt.legend(loc=9, bbox_to_anchor=(0.5, -0.05), ncol=3) 

      
    
    if origin==-2 or origin == -3 or (origin==1 and sender=='SHIPcal'):
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'savMonths.png', format='png', dpi=imageQlty)  
    if origin==0:
        plt.show()
        return output_excel


def SL_S_PDR_Plot(sender,origin,step_sim,steps_sim,SD_min_energy,SD_max_energy,Q_prod,Q_prod_steam,SD_energy,T_in_K,T_out_K,T_SD_K,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    fig.suptitle('Direct steam Generation RECIRCULATION', fontsize=14, fontweight='bold')
    ax1 = fig.add_subplot(111)  
    ax1 .plot(step_sim, Q_prod,'m:',label="Producción solar")
    ax1 .plot(step_sim, Q_prod_steam,'g:',label="Producción vapor")    
    ax1 .plot(step_sim, SD_energy,color='orange',label="Energia en SD")
    ax1 .axhline(y=SD_min_energy,xmin=0,xmax=steps_sim,c="black",linewidth=0.5,zorder=0)
    ax1 .axhline(y=SD_max_energy,xmin=0,xmax=steps_sim,c="black",linewidth=0.5,zorder=0)
    ax1.set_ylim([0,max(SD_max_energy,max(Q_prod_steam))*1.1])
    ax1.set_xlabel('Simulación (hora del año)')
    ax1.set_ylabel('Energía - kWh')
    plt.legend(bbox_to_anchor=(1.15, .5), loc=2, borderaxespad=0.)
    ax2 = ax1.twinx()          
    ax2 .plot(step_sim, T_in_K-273,'-',color = '#1F85DE',label="Temp_in Solar")
    ax2 .plot(step_sim, T_out_K-273,'-',color = 'red',label="Temp_out Solar")
    ax2 .plot(step_sim, T_SD_K-273,':',color = 'orange',label="Temp_alm")
    ax2.set_ylabel('Temp - C')
    ax2.set_ylim([0,(np.max([np.max(T_SD_K),np.max(T_out_K)])-273)*1.2])
    plt.legend(bbox_to_anchor=(1.15, 1), loc=2, borderaxespad=0.)    

    # output1=pd.DataFrame(flow_rate_kgs)
    # output1.columns=['Flow_rate']
    # output2=pd.DataFrame(T_in_K)
    # output2.columns=['T_in_K']
    # output3=pd.DataFrame(T_out_K)
    # output3.columns=['T_out_K']
    # output_excel_FlowratesTemps=pd.concat([output1,output2,output3], axis=1)

    if origin==-2 or origin == -3:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'flowrates.png', format='png', dpi=imageQlty)

