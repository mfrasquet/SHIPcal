# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 12:25:12 2020

@author: Danieel
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


def thetaAnglesPlot2(itercontrol,sender,origin,step_sim,steps_sim,theta_i_deg,theta_transv_deg,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    fig.suptitle('Ángulos theta', fontsize=14, fontweight='bold')
    ax1 = fig.add_subplot(111)  
    ax1 .plot(step_sim, theta_i_deg,'.r-',label="Ang_incidencia")
    ax1 .plot(step_sim, theta_transv_deg,'.b-',label="Incidencia_transversal")
    ax1 .axhline(y=0,xmin=0,xmax=steps_sim,c="blue",linewidth=0.5,zorder=0)
    if itercontrol=='paso_10min':
        ax1.set_xlabel('Simulación: pasos diezminutales')
    elif itercontrol=='paso_15min':
        ax1.set_xlabel('Simulación: pasos quinceminutales')
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

def IAMAnglesPlot2(itercontrol,sender,origin,step_sim,IAM_long,IAM_t,IAM,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    fig.suptitle('IAMs', fontsize=14, fontweight='bold')
    ax2 = fig.add_subplot(111)         
    ax2 .plot(step_sim, IAM_long,'.-',color = 'b',label="IAM_long")
    ax2 .plot(step_sim, IAM_t,'.-',color = 'r',label="IAM_transv")
    ax2 .plot(step_sim, IAM,'.-',color = '#39B8E3',label="IAM")
    if itercontrol=='paso_10min':
        ax2.set_xlabel('Simulación: pasos diezminutales')
    elif itercontrol=='paso_15min':
        ax2.set_xlabel('Simulación: pasos quinceminutales')
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
    
def demandVsRadiation2(itercontrol,sender,origin,lang,step_sim,Demand,Q_prod,Q_prod_lim,Q_prod_rec,steps_sim,DNI,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    # print(len(step_sim))
    # print(len(Demand))
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
        if itercontrol=='paso_10min':
            ax1.set_xlabel('Simulación: pasos diezminutales')
        elif itercontrol=='paso_15min':
            ax1.set_xlabel('Simulación: pasos quinceminutales')
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
        if itercontrol=='paso_10min':
            ax1.set_xlabel('Simulation: ten-minutes´s steps')
        elif itercontrol=='paso_15min':
            ax1.set_xlabel('Simulation: fifteen-minutes´s steps')
     
        ax1.set_ylabel('Demand - kWh',color="blue")
        ax1.set_ylim([0,np.max(Demand)*1.2])
        plt.legend(loc='upper left', borderaxespad=0.)
        ax2 = ax1.twinx()          
        ax2 .plot(step_sim, DNI,'.-',color = 'orange',label="DNI")
        ax2.set_ylabel('Solar Radiaton - W/m2',color='red')
        plt.legend(loc='upper right', borderaxespad=0.)
    
    if origin==-2 or origin == -3 or origin == 1:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'demandProduction.png', format='png', dpi=imageQlty)


def flowRatesPlot2(itercontrol,sender,origin,step_sim,steps_sim,flow_rate_kgs,flow_rate_rec,num_loops,flowDemand,flowToHx,flowToMix,m_dot_min_kgs,T_in_K,T_toProcess_C,T_out_K,T_alm_K,plotPath,imageQlty,**kwargs):
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
    if itercontrol=='paso_10min':
        ax1.set_xlabel('Simulación: pasos diezminutales')
    elif itercontrol=='paso_15min':
        ax1.set_xlabel('Simulación: pasos quinceminutales')
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
    
    if origin==-2 or origin == -3 or origin==1:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'flowrates.png', format='png', dpi=imageQlty)
    
def prodWinterPlot2(itercontrol,sender,origin,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if itercontrol=='paso_10min':
        factor=6
    elif itercontrol=='paso_15min':
        factor=4
    if lang=="spa": 
        fig.suptitle('Producción solar primera semana Enero', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)
        
        ax1 .plot(np.arange(167*factor), DNI[0:167*factor],color='#CA6A16',linestyle='solid',label="Radiación solar")
        if itercontrol=='paso_10min':
            ax1.set_xlabel('simulación: pasos diezminutales')
        elif itercontrol=='paso_15min':
            ax1.set_xlabel('simulación: pasos quinceminutales')
        ax1.set_ylabel('Radiación Solar - W/m2')
        ax1.set_ylim([0,1200])
        plt.legend(loc='upper left', borderaxespad=0.,frameon=False)
        ax2 = ax1.twinx()   
        ax2.fill_between( np.arange(167*factor), Demand[0:167*factor], color="grey", alpha=0.2,label="Demanda")
        ax2 .plot(np.arange(167*factor), Demand[0:167*factor],'.-',color = '#362510',label="Demanda")
        if sender =='CIMAV':
            ax2 .plot(np.arange(167*factor), Q_prod[0:167*factor],'.-',color = 'red',label="Disipación")
        else:
            ax2 .plot(np.arange(167*factor), Q_prod[0:167*factor],'.-',color = 'red',label="Desenfoque")
        ax2 .plot(np.arange(167*factor), Q_prod_lim[0:167*factor],'.-',color = 'blue',label="Producción solar")
        if type_integration=="SL_L_PS" or type_integration=='SL_S_FWS':
            ax2 .plot(np.arange(167*factor), Q_charg[0:167*factor],'.-',color = '#FFAE00',label="Carga")
            ax2 .plot(np.arange(167*factor), Q_discharg[0:167*factor],'.-',color = '#2EAD23',label="Descarga")
        ax2.set_ylabel('Producción y Demanda - kWh')
        ax2.set_ylim([0,np.max(Q_prod)*4.2])
        plt.legend(bbox_to_anchor=(1.00, 1), loc=1, borderaxespad=0.)
    #    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        plt.tight_layout()
    if lang=="eng": 
        fig.suptitle('Solar production first week January', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)
        
        ax1 .plot(np.arange(167*factor), DNI[0:167*factor],color='#CA6A16',linestyle='solid',label="Solar Radiation")
        if itercontrol=='paso_10min':
            ax1.set_xlabel('ten-minutes´s steps')
        elif itercontrol=='paso_15min':
            ax1.set_xlabel('fifteen-minutes´s steps')
        ax1.set_ylabel('Solar Radiation - W/m2')
        ax1.set_ylim([0,1200])
        plt.legend(loc='upper left', borderaxespad=0.,frameon=False)
        ax2 = ax1.twinx()
        plt.fill_between( np.arange(167*factor), Demand[0:167*factor], color="grey", alpha=0.2,label="Demand")          
        ax2 .plot(np.arange(167*factor), Demand[0:167*factor],'.-',color = '#362510',label="Demand")
        ax2 .plot(np.arange(167*factor), Q_prod[0:167*factor],'.-',color = 'red',label="Defocused")
        ax2 .plot(np.arange(167*factor), Q_prod_lim[0:167*factor],'.-',color = 'blue',label="Solar production")
        if type_integration=="SL_L_PS" or type_integration=='SL_S_FWS':
            ax2 .plot(np.arange(167*factor), Q_charg[0:167*factor],'.-',color = '#FFAE00',label="Charge")
            ax2 .plot(np.arange(167*factor), Q_discharg[0:167*factor],'.-',color = '#2EAD23',label="Discharge")
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
 
def prodSummerPlot2(itercontrol,sender,origin,lang,Demand,Q_prod,Q_prod_lim,type_integration,Q_charg,Q_discharg,DNI,plotPath,imageQlty,**kwargs):
    fig = plt.figure()
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    
    if itercontrol=='paso_10min':
        factor=6
    elif itercontrol=='paso_15min':
        factor=4
    
    if lang=="spa":         
        fig.suptitle('Producción solar primera semana Junio', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)

        ax1 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), DNI[3624*factor:3791*factor],color='#CA6A16',linestyle='solid',label="Radiación solar")
        if itercontrol=='paso_10min':
            ax1.set_xlabel('simulación: pasos diezminutales')
        elif itercontrol=='paso_15min':
            ax1.set_xlabel('simulación: pasos quinceminutales')
        ax1.set_ylabel('Radiación Solar - W/m2')
        ax1.set_ylim([0,1200])
        plt.legend(loc='upper left', borderaxespad=0.,frameon=False)
        ax2 = ax1.twinx()   
        ax2.fill_between( np.arange(3624*factor,3624*factor+167*factor,1), Demand[3624*factor:3791*factor], color="grey", alpha=0.2,label="Demanda")
        ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Demand[3624*factor:3791*factor],'.-',color = '#362510',label="Demanda")
        if sender =='CIMAV':
            ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Q_prod[3624*factor:3791*factor],'.-',color = 'red',label="Disipación")
        else:
            ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Q_prod[3624*factor:3791*factor],'.-',color = 'red',label="Desenfoque")
        ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Q_prod_lim[3624*factor:3791*factor],'.-',color = 'blue',label="Producción solar")
        if type_integration=="SL_L_PS" or type_integration=='SL_S_FWS':
            ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Q_charg[3624*factor:3791*factor],'.-',color = '#FFAE00',label="Carga")
            ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Q_discharg[3624*factor:3791*factor],'.-',color = '#2EAD23',label="Descarga")
       
        ax2.set_ylabel('Producción y Demanda - kWh')
        ax2.set_ylim([0,np.max(Q_prod)*4.2])
        plt.legend(bbox_to_anchor=(1.00, 1), loc=1, borderaxespad=0.)
        plt.tight_layout()
    if lang=="eng":

        fig.suptitle('Solar production first week of June', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)
       
        ax1 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), DNI[3624*factor:3791*factor],color='#CA6A16',linestyle='solid',label="Solar Radiation")
        if itercontrol=='paso_10min':
            ax1.set_xlabel('ten-minutes´s steps')
        elif itercontrol=='paso_15min':
            ax1.set_xlabel('fifteen-minutes´s steps')
        ax1.set_ylabel('Solar Radiation - W/m2')
        ax1.set_ylim([0,1200])
        plt.legend(loc='upper left', borderaxespad=0.,frameon=False)
        ax2 = ax1.twinx()
        ax2.fill_between( np.arange(3624*factor,3624*factor+167*factor,1), Demand[3624*factor:3791*factor], color="grey", alpha=0.2,label="Demand")          
        ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Demand[3624*factor:3791*factor],'.-',color = '#362510',label="Demand")
        ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Q_prod[3624*factor:3791*factor],'.-',color = 'red',label="Defocused")
        ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Q_prod_lim[3624*factor:3791*factor],'.-',color = 'blue',label="Solar Production")
        if type_integration=="SL_L_PS" or type_integration=='SL_S_FWS':
            ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Q_charg[3624*factor:3791*factor],'.-',color = '#FFAE00',label="Charge")
            ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Q_discharg[3624*factor:3791*factor],'.-',color = '#2EAD23',label="Discharge")
       
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


def productionSolar2(itercontrol,sender,origin,lang,step_sim,DNI,m_dot_min_kgs,steps_sim,Demand,Q_prod,Q_prod_lim,Q_charg,Q_discharg,type_integration,plotPath,imageQlty,**kwargs):
    fig = plt.figure(figsize=(14, 3.5))
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if lang=="spa": 
        fig.suptitle('Producción anual', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)  
        ax1 .plot(step_sim, DNI,'.r-',label="Radiación solar")
#        ax1 .axhline(y=m_dot_min_kgs,xmin=0,xmax=steps_sim,c="black",linewidth=0.5,zorder=0)
        if itercontrol=='paso_10min':
            ax1.set_xlabel('Simulación: pasos diezminutales')
        elif itercontrol=='paso_15min':
            ax1.set_xlabel('Simulación: pasos quinceminutales')
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
        if itercontrol=='paso_10min':
            ax1.set_xlabel('Simulation: ten-minutes´s steps')
        elif itercontrol=='paso_15min':
            ax1.set_xlabel('Simulation: fifteen-minutes´s steps')
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
       
    
def storageWinter2(itercontrol,sender,origin,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty,**kwargs):
    fig = plt.figure(figsize=(14, 3.5))
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if itercontrol=='paso_10min':
        factor=6
    elif itercontrol=='paso_15min':
        factor=4
    
    if lang=="spa":
        fig.suptitle('Almacenamiento primera semana Enero', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)  
        plt.fill_between( np.arange(167*factor), Demand[0:167*factor], color="grey", alpha=0.2)
        
        plt.bar(np.arange(167*factor), np.array(Q_prod[0:167*factor])-np.array(Q_charg[0:167*factor]),color = 'blue',label="Producción Solar",align='center')
#        ax1 .plot(np.arange(167), Q_prod_lim[0:167],color = 'blue',label="Energía suministrada",linewidth=4)
#        ax1 .plot(np.arange(167), Q_useful[0:167],color = 'green',label="Energía útil",linewidth=2)
        
        ax1 .plot(np.arange(167*factor), Demand[0:167*factor],color = '#362510',label="Demanda",linewidth=2.0)
        if sender =='CIMAV':
            plt.bar(np.arange(167*factor), Q_defocus[0:167*factor],color = 'red',label="Disipación",bottom=np.array(Q_prod[0:167*factor])-np.array(Q_defocus[0:167*factor]),align='center')
        else:
            plt.bar(np.arange(167*factor), Q_defocus[0:167*factor],color = 'red',label="Desenfoque",bottom=np.array(Q_prod[0:167*factor])-np.array(Q_defocus[0:167*factor]),align='center')
           
        plt.bar(np.arange(167*factor), Q_charg[0:167*factor],color = '#FFAE00',label="Carga",bottom=np.array(Q_prod[0:167*factor])-np.array(Q_charg[0:167*factor])-np.array(Q_defocus[0:167*factor]),align='center')
    
        plt.bar(np.arange(167*factor), Q_discharg[0:167*factor],color = '#2EAD23',label="Descarga",bottom=np.array(Q_prod[0:167*factor]),align='center')
         
        ax1.set_ylabel('Producción & Demanda - kWh')
        ax1.set_ylim([0,np.max([np.max(Q_prod[0:167*factor]),np.max(Demand[0:167*factor])])*1.1])
        ax1.set_xlim([0,167*factor])
        plt.legend(loc='upper left', borderaxespad=0.)
    
        ax2 = ax1.twinx()  
        if type_integration=="SL_L_S" or type_integration=="SL_L_S_PH":
            ax2 .plot(np.arange(167*factor), np.array(T_alm_K[0:167*factor])-273,'r',label="Temperatura",linewidth=2.0)
        ax2 .plot(np.arange(167*factor), SOC[0:167*factor],color='orange',linestyle=':',label="Carga del almacenamiento",linewidth=2.0)
        if itercontrol=='paso_10min':
            ax2.set_xlabel('simulación: pasos diezminutales')
        elif itercontrol=='paso_15min':
            ax2.set_xlabel('simulación: pasos quinceminutales')
        ax2.set_ylabel('Estado de carga almacenamiento %',color = '#CA6A16')
        ax2.set_ylim([0,101])
        ax2.set_xlim([0,167*factor])

    if lang=="eng":
        fig.suptitle('Storage during the first week of January', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)  
        plt.fill_between( np.arange(167*factor), Demand[0:167*factor], color="grey", alpha=0.2)
        plt.bar(np.arange(167*factor), np.array(Q_prod[0:167*factor])-np.array(Q_charg[0:167*factor]),color = 'blue',label="Solar Production",align='center')
#        ax1 .plot(np.arange(167), Q_prod_lim[0:167],color = 'blue',label="Net production",linewidth=4)
#        ax1 .plot(np.arange(167), Q_useful[0:167],color = 'green',label="Useful energy",linewidth=2)
        
        ax1 .plot(np.arange(167*factor), Demand[0:167*factor],color = '#362510',label="Demand",linewidth=2.0)
        plt.bar(np.arange(167*factor), Q_defocus[0:167*factor],color = 'red',label="Defocused",bottom=np.array(Q_prod[0:167*factor])-np.array(Q_defocus[0:167*factor]),align='center')
           
        plt.bar(np.arange(167*factor), Q_charg[0:167*factor],color = '#FFAE00',label="Charge",bottom=np.array(Q_prod[0:167*factor])-np.array(Q_charg[0:167*factor])-np.array(Q_defocus[0:167*factor]),align='center')
    
        plt.bar(np.arange(167*factor), Q_discharg[0:167*factor],color = '#2EAD23',label="Discharge",bottom=np.array(Q_prod[0:167*factor]),align='center')
         
        ax1.set_ylabel('Production & Demand - kWh')
        ax1.set_ylim([0,np.max([np.max(Q_prod[0:167*factor]),np.max(Demand[0:167*factor])])*1.1])
        ax1.set_xlim([0,167*factor])

        plt.legend(loc='upper left', borderaxespad=0.)
        
        ax2 = ax1.twinx()
        if type_integration=="SL_L_S" or type_integration=="SL_L_S_PH":
            ax2 .plot(np.arange(167*factor), np.array(T_alm_K[0:167*factor])-273,'r',label="Temperature",linewidth=2.0)
      
        ax2 .plot(np.arange(167*factor), SOC[0:167*factor],color='orange',linestyle=':',label="Storage's state of charge",linewidth=2.0)
        if itercontrol=='paso_10min':
            ax2.set_xlabel('simulation: ten-minutes´s steps')
        elif itercontrol=='paso_15min':
            ax2.set_xlabel('simulation: fifteen-minutes´s steps')  
        
        ax2.set_ylabel("Storage's state of charge %",color = '#CA6A16')
        ax2.set_ylim([0,101])
        ax2.set_xlim([0,167*factor])

    
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

def storageSummer2(itercontrol,sender,origin,lang,Q_prod,Q_charg,Q_prod_lim,Q_useful,Demand,Q_defocus,Q_discharg,type_integration,T_alm_K,SOC,plotPath,imageQlty,**kwargs):
    fig = plt.figure(figsize=(14, 3.5))
    #np.array(in list) is because Django need it since Q_prod, Q_prod_lim,.. are passed as lists
    if origin==-2 or origin == -3:
        fig.patch.set_alpha(0)
    if itercontrol=='paso_10min':
        factor=6
    elif itercontrol=='paso_15min':
        factor=4
    if lang=="spa":
        fig.suptitle('Almacenamiento primera semana Junio', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)  
    
        plt.fill_between( np.arange(3624*factor,3624*factor+167*factor,1), Demand[3624*factor:3791*factor], color="grey", alpha=0.2)

        plt.bar((np.arange(3624*factor,3624*factor+167*factor,1)), np.array(Q_prod[3624*factor:3791*factor])-np.array(Q_charg[3624*factor:3791*factor]),color = 'blue',label="Producción Solar",align='center')
        #ax1 .plot((np.arange(3624,3624+167,1)), Q_prod_lim[3624:3791],color = 'blue',label="Energía suministrada",linewidth=4)
        #ax1 .plot((np.arange(3624,3624+167,1)), Q_useful[3624:3791],color = 'green',label="Energía útil",linewidth=2)
        
        ax1 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Demand[3624*factor:3791*factor],color = '#362510',label="Demanda",linewidth=2.0)
        if sender =='CIMAV':
            plt.bar((np.arange(3624*factor,3624*factor+167*factor,1)), Q_defocus[3624*factor:3791*factor],color = 'red',label="Disipación",bottom=np.array(Q_prod[3624*factor:3791*factor])-np.array(Q_defocus[3624*factor:3791*factor]),align='center')
        else:
            plt.bar((np.arange(3624*factor,3624*factor+167*factor,1)), Q_defocus[3624*factor:3791*factor],color = 'red',label="Desenfoque",bottom=np.array(Q_prod[3624*factor:3791*factor])-np.array(Q_defocus[3624*factor:3791*factor]),align='center')
           
        plt.bar((np.arange(3624*factor,3624*factor+167*factor,1)), Q_charg[3624*factor:3791*factor],color = '#FFAE00',label="Carga",bottom=np.array(Q_prod[3624*factor:3791*factor])-np.array(Q_charg[3624*factor:3791*factor])-np.array(Q_defocus[3624*factor:3791*factor]),align='center')
    
        plt.bar((np.arange(3624*factor,3624*factor+167*factor,1)), Q_discharg[3624*factor:3791*factor],color = '#2EAD23',label="Descarga",bottom=Q_prod[3624*factor:3791*factor],align='center')
         
        ax1.set_ylabel('Producción & Demanda - kWh')
        ax1.set_ylim([0,np.max([np.max(Q_prod[3624*factor:3791*factor]),np.max(Demand[3624*factor:3791*factor])])*1.1])
        ax1.set_xlim([3624*factor,3624*factor+167*factor])
        ax1.legend(loc='upper left', borderaxespad=0.).set_zorder(99)
        
        
        
        ax2 = ax1.twinx()
        if type_integration=="SL_L_S" or type_integration=="SL_L_S_PH":
             ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), np.array(T_alm_K[3624*factor:3791*factor])-273,'r',label="Carga del almacenamiento",linewidth=2.0,zorder=11)
        ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), SOC[3624*factor:3791*factor],color='orange',linestyle=':',label="Carga del almacenamiento",linewidth=2.0,zorder=11)
        if itercontrol=='paso_10min':
            ax2.set_xlabel('simulación: pasos diezminutales')
        elif itercontrol=='paso_15min':
            ax2.set_xlabel('simulación: pasos quinceminutales')
        ax2.set_ylabel('Estado de carga almacenamiento %',color = '#CA6A16')
        ax2.set_ylim([0,101])
        ax2.set_xlim([3624*factor,3624*factor+167*factor])
        
        
    if lang=="eng":
        fig.suptitle('Storage during the first week of June', fontsize=14, fontweight='bold',y=1)
        ax1 = fig.add_subplot(111)  
        plt.fill_between( np.arange(3624*factor,3624*factor+167*factor,1), Demand[3624*factor:3791*factor], color="grey", alpha=0.2)
        plt.bar((np.arange(3624*factor,3624*factor+167*factor,1)), np.array(Q_prod[3624*factor:3791*factor])-np.array(Q_charg[3624*factor:3791*factor]),color = 'blue',label="Solar Production",align='center')
        #ax1 .plot((np.arange(3624,3624+167,1)), Q_prod_lim[3624:3791],color = 'blue',label="Net Production",linewidth=4)
        #ax1 .plot((np.arange(3624,3624+167,1)), Q_useful[3624:3791],color = 'green',label="Useful energy",linewidth=2)
        
        ax1 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), Demand[3624*factor:3791*factor],color = '#362510',label="Demand",linewidth=2.0)
        plt.bar((np.arange(3624*factor,3624*factor+167*factor,1)), Q_defocus[3624*factor:3791*factor],color = 'red',label="Defocused",bottom=np.array(Q_prod[3624*factor:3791*factor])-np.array(Q_defocus[3624*factor:3791*factor]),align='center')
           
        plt.bar((np.arange(3624*factor,3624*factor+167*factor,1)), Q_charg[3624*factor:3791*factor],color = '#FFAE00',label="Charge",bottom=np.array(Q_prod[3624*factor:3791*factor])-np.array(Q_charg[3624*factor:3791*factor])-np.array(Q_defocus[3624*factor:3791*factor]),align='center')
    
        plt.bar((np.arange(3624*factor,3624*factor+167*factor,1)), Q_discharg[3624*factor:3791*factor],color = '#2EAD23',label="Discharge",bottom=Q_prod[3624*factor:3791*factor],align='center')
         
        ax1.set_ylabel('Production & Demand - kWh')
        ax1.set_ylim([0,np.max([np.max(Q_prod[3624*factor:3791*factor]),np.max(Demand[3624*factor:3791*factor])])*1.1])
        ax1.set_xlim([3624*factor,3624*factor+167*factor])
    
        plt.legend(loc='upper left', borderaxespad=0.)
        
        ax2 = ax1.twinx()  
        ax2 .plot((np.arange(3624*factor,3624*factor+167*factor,1)), SOC[3624*factor:3791*factor],color='orange',linestyle=':',label="Storage's state of charge %",linewidth=2.0)
        if itercontrol=='paso_10min':
            ax2.set_xlabel('simulation: ten-minutes´s steps')
        elif itercontrol=='paso_15min':
            ax2.set_xlabel('simulation: fifteen-minutes´s steps')
        ax2.set_ylabel("Storage's state of charge %",color = '#CA6A16')
        ax2.set_ylim([0,101])
        ax2.set_xlim([3624*factor,3624*factor+167*factor])
    
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

def storageNonAnnual2(itercontrol,sender,origin,SOC,Q_useful,Q_prod,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty,**kwargs):
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
    if itercontrol=='paso_10min':
        ax2.set_xlabel('simulación: pasos diezminutales')
    elif itercontrol=='paso_15min':
        ax2.set_xlabel('simulación: pasos quinceminutales')
    ax2.set_ylabel('Estado de carga almacenamiento %',color = '#CA6A16')
    ax2.set_ylim([0,101])
    ax2.set_xlim([0,steps_sim])
   
    plt.tight_layout()
    
    
    if origin==-2 or origin == -3 or origin == 1:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'almacenamiento_Anual.png', format='png', dpi=imageQlty)
        
def storageNonAnnualSL_S_PDR2(itercontrol,sender,origin,SOC,Q_useful,Q_prod_steam,Q_prod,Q_drum,Q_charg,Q_prod_lim,step_sim,Demand,Q_defocus,Q_discharg,steps_sim,plotPath,imageQlty,**kwargs):
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
    if itercontrol=='paso_10min':
        ax2.set_xlabel('simulación: pasos diezminutales')
    elif itercontrol=='paso_15min' :
        ax2.set_xlabel('simulación: pasos quinceminutales')
    ax2.set_ylabel('Estado de carga almacenamiento %',color = '#CA6A16')
    ax2.set_ylim([0,101])
    ax2.set_xlim([0,steps_sim])

    plt.tight_layout()


    if origin==-2 or origin == -3 or origin == 1:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'almacenamiento_Anual.png', format='png', dpi=imageQlty)


def arraysMonth2(itercontrol,Q_prod,Q_prod_lim,DNI,Demand,**kwargs):
 #Para resumen mensual  
    if itercontrol=='paso_10min':
        steps=52560
        factor=6
    elif itercontrol=='paso_15min':
        steps==35040
        factor=4
    Ene_prod=np.zeros(steps)
    Feb_prod=np.zeros(steps)
    Mar_prod=np.zeros(steps)
    Abr_prod=np.zeros(steps)
    May_prod=np.zeros(steps)
    Jun_prod=np.zeros(steps)
    Jul_prod=np.zeros(steps)
    Ago_prod=np.zeros(steps)
    Sep_prod=np.zeros(steps)
    Oct_prod=np.zeros(steps)
    Nov_prod=np.zeros(steps)
    Dic_prod=np.zeros(steps)
    Ene_prod_lim=np.zeros(steps)
    Feb_prod_lim=np.zeros(steps)
    Mar_prod_lim=np.zeros(steps)
    Abr_prod_lim=np.zeros(steps)
    May_prod_lim=np.zeros(steps)
    Jun_prod_lim=np.zeros(steps)
    Jul_prod_lim=np.zeros(steps)
    Ago_prod_lim=np.zeros(steps)
    Sep_prod_lim=np.zeros(steps)
    Oct_prod_lim=np.zeros(steps)
    Nov_prod_lim=np.zeros(steps)
    Dic_prod_lim=np.zeros(steps)
    Ene_DNI=np.zeros(steps)
    Feb_DNI=np.zeros(steps)
    Mar_DNI=np.zeros(steps)
    Abr_DNI=np.zeros(steps)
    May_DNI=np.zeros(steps)
    Jun_DNI=np.zeros(steps)
    Jul_DNI=np.zeros(steps)
    Ago_DNI=np.zeros(steps)
    Sep_DNI=np.zeros(steps)
    Oct_DNI=np.zeros(steps)
    Nov_DNI=np.zeros(steps)
    Dic_DNI=np.zeros(steps)
    Ene_demd=np.zeros(steps)
    Feb_demd=np.zeros(steps)
    Mar_demd=np.zeros(steps)
    Abr_demd=np.zeros(steps)
    May_demd=np.zeros(steps)
    Jun_demd=np.zeros(steps)
    Jul_demd=np.zeros(steps)
    Ago_demd=np.zeros(steps)
    Sep_demd=np.zeros(steps)
    Oct_demd=np.zeros(steps)
    Nov_demd=np.zeros(steps)
    Dic_demd=np.zeros(steps)
    
  
    
    for i in range(0,steps):
        if (i<=744*factor-1):
            Ene_prod[i]=Q_prod[i]
            Ene_prod_lim[i]=Q_prod_lim[i]
            Ene_DNI[i]=DNI[i]
            Ene_demd[i]=Demand[i]
        if (i>744*factor-1) and (i<=1416*factor-1):
            Feb_prod[i]=Q_prod[i]
            Feb_prod_lim[i]=Q_prod_lim[i]
            Feb_DNI[i]=DNI[i]
            Feb_demd[i]=Demand[i]
        if (i>1416*factor-1) and (i<=2160*factor-1):
            Mar_prod[i]=Q_prod[i]
            Mar_prod_lim[i]=Q_prod_lim[i]
            Mar_DNI[i]=DNI[i]
            Mar_demd[i]=Demand[i]
        if (i>2160*factor-1) and (i<=2880*factor-1):
            Abr_prod[i]=Q_prod[i]
            Abr_prod_lim[i]=Q_prod_lim[i]
            Abr_DNI[i]=DNI[i]
            Abr_demd[i]=Demand[i]
        if (i>2880*factor-1) and (i<=3624*factor-1):
            May_prod[i]=Q_prod[i]
            May_prod_lim[i]=Q_prod_lim[i]
            May_DNI[i]=DNI[i] 
            May_demd[i]=Demand[i]
        if (i>3624*factor-1) and (i<=4344*factor-1):
            Jun_prod[i]=Q_prod[i]
            Jun_prod_lim[i]=Q_prod_lim[i]
            Jun_DNI[i]=DNI[i] 
            Jun_demd[i]=Demand[i]
        if (i>4344*factor-1) and (i<=5088*factor-1):
            Jul_prod[i]=Q_prod[i]
            Jul_prod_lim[i]=Q_prod_lim[i]
            Jul_DNI[i]=DNI[i]
            Jul_demd[i]=Demand[i]
        if (i>5088*factor-1) and (i<=5832*factor-1):
            Ago_prod[i]=Q_prod[i]
            Ago_prod_lim[i]=Q_prod_lim[i]
            Ago_DNI[i]=DNI[i] 
            Ago_demd[i]=Demand[i]
        if (i>5832*factor-1) and (i<=6552*factor-1):
            Sep_prod[i]=Q_prod[i]
            Sep_prod_lim[i]=Q_prod_lim[i]
            Sep_DNI[i]=DNI[i]
            Sep_demd[i]=Demand[i]
        if (i>6552*factor-1) and (i<=7296*factor-1):
            Oct_prod[i]=Q_prod[i]
            Oct_prod_lim[i]=Q_prod_lim[i]
            Oct_DNI[i]=DNI[i]
            Oct_demd[i]=Demand[i]
        if (i>7296*factor-1) and (i<=8016*factor-1):
            Nov_prod[i]=Q_prod[i]
            Nov_prod_lim[i]=Q_prod_lim[i]
            Nov_DNI[i]=DNI[i]
            Nov_demd[i]=Demand[i]
        if (i>8016*factor-1):
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

def prodMonths2(itercontrol,sender,origin,Q_prod,Q_prod_lim,DNI,Demand,lang,plotPath,imageQlty,**kwargs):
    array_de_meses,array_de_meses_lim,array_de_DNI,array_de_demd,array_de_fraction=arraysMonth2(itercontrol,Q_prod,Q_prod_lim,DNI,Demand)
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
    
    
def arrays_Savings_Month2(itercontrol,Q_prod_lim,Demand,Fuel_price,Boiler_eff,**kwargs):
 #Para resumen mensual      
    if itercontrol=='paso_10min':
        steps=52560
        factor=6
    elif itercontrol=='paso_15min':
        steps==35040
        factor=4
    Ene_sav_lim=np.zeros(steps)
    Feb_sav_lim=np.zeros(steps)
    Mar_sav_lim=np.zeros(steps)
    Abr_sav_lim=np.zeros(steps)
    May_sav_lim=np.zeros(steps)
    Jun_sav_lim=np.zeros(steps)
    Jul_sav_lim=np.zeros(steps)
    Ago_sav_lim=np.zeros(steps)
    Sep_sav_lim=np.zeros(steps)
    Oct_sav_lim=np.zeros(steps)
    Nov_sav_lim=np.zeros(steps)
    Dic_sav_lim=np.zeros(steps)
    Ene_demd=np.zeros(steps)
    Feb_demd=np.zeros(steps)
    Mar_demd=np.zeros(steps)
    Abr_demd=np.zeros(steps)
    May_demd=np.zeros(steps)
    Jun_demd=np.zeros(steps)
    Jul_demd=np.zeros(steps)
    Ago_demd=np.zeros(steps)
    Sep_demd=np.zeros(steps)
    Oct_demd=np.zeros(steps)
    Nov_demd=np.zeros(steps)
    Dic_demd=np.zeros(steps)
    Ene_frac=np.zeros(steps)
    Feb_frac=np.zeros(steps)
    Mar_frac=np.zeros(steps)
    Abr_frac=np.zeros(steps)
    May_frac=np.zeros(steps)
    Jun_frac=np.zeros(steps)
    Jul_frac=np.zeros(steps)
    Ago_frac=np.zeros(steps)
    Sep_frac=np.zeros(steps)
    Oct_frac=np.zeros(steps)
    Nov_frac=np.zeros(steps)
    Dic_frac=np.zeros(steps)

        
    for i in range(0,steps):
        if (i<=744*factor-1):
            Ene_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Ene_demd[i]=Fuel_price*Demand[i]
            if Ene_demd[i] == 0:
                Ene_frac[i] = 0
            else:
                Ene_frac[i]=Ene_sav_lim[i]/Ene_demd[i]
        if (i>744*factor-1) and (i<=1416*factor-1):
            Feb_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Feb_demd[i]=Fuel_price*Demand[i]
            if Feb_demd[i] == 0:
                Feb_frac[i] = 0
            else:
                Feb_frac[i]=Feb_sav_lim[i]/Feb_demd[i]
        if (i>1416*factor-1) and (i<=2160*factor-1):
            Mar_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Mar_demd[i]=Fuel_price*Demand[i]
            if Mar_demd[i] == 0:
                Mar_frac[i] = 0
            else:
                Mar_frac[i]=Mar_sav_lim[i]/Mar_demd[i]
        if (i>2160*factor-1) and (i<=2880*factor-1):
            Abr_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Abr_demd[i]=Fuel_price*Demand[i]
            if Abr_demd[i] == 0:
                Abr_frac[i] = 0
            else:
                Abr_frac[i]=Abr_sav_lim[i]/Abr_demd[i]
        if (i>2880*factor-1) and (i<=3624*factor-1):
            May_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            May_demd[i]=Fuel_price*Demand[i]
            if May_demd[i] == 0:
                May_frac[i] = 0
            else:
                May_frac[i]=May_sav_lim[i]/May_demd[i]
        if (i>3624*factor-1) and (i<=4344*factor-1):
            Jun_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Jun_demd[i]=Fuel_price*Demand[i]
            if Jun_demd[i] == 0:
                Jun_frac[i] = 0
            else:
                Jun_frac[i]=Jun_sav_lim[i]/Jun_demd[i]
        if (i>4344*factor-1) and (i<=5088*factor-1):
            Jul_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Jul_demd[i]=Fuel_price*Demand[i]
            if Jul_demd[i] == 0:
                Jul_frac[i] = 0
            else:
                Jul_frac[i]=Jul_sav_lim[i]/Jul_demd[i]
        if (i>5088*factor-1) and (i<=5832*factor-1):
            Ago_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Ago_demd[i]=Fuel_price*Demand[i]
            if Ago_demd[i] == 0:
                Ago_frac[i] = 0
            else:
                Ago_frac[i]=Ago_sav_lim[i]/Ago_demd[i]
        if (i>5832*factor-1) and (i<=6552*factor-1):
            Sep_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Sep_demd[i]=Fuel_price*Demand[i]
            if Sep_demd[i] == 0:
                Sep_frac[i] = 0
            else:
                Sep_frac[i]=Sep_sav_lim[i]/Sep_demd[i]
        if (i>6552*factor-1) and (i<=7296*factor-1):
            Oct_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Oct_demd[i]=Fuel_price*Demand[i]
            if Oct_demd[i] == 0:
                Oct_frac[i] = 0
            else:
                Oct_frac[i]=Oct_sav_lim[i]/Oct_demd[i]
        if (i>7296*factor-1) and (i<=8016*factor-1):
            Nov_sav_lim[i]=Fuel_price*Q_prod_lim[i]/Boiler_eff
            Nov_demd[i]=Fuel_price*Demand[i]
            if Nov_demd[i] == 0:
                Nov_frac[i] = 0
            else:
                Nov_frac[i]=Nov_sav_lim[i]/Nov_demd[i]
        if (i>8016*factor-1):
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

    
def savingsMonths2(itercontrol,sender,origin,Q_prod_lim,Demand,Fuel_price,Boiler_eff,lang,plotPath,imageQlty,**kwargs):
    array_de_meses_lim,array_de_demd,array_de_fraction=arrays_Savings_Month2(itercontrol,Q_prod_lim,Demand,Fuel_price,Boiler_eff)
  
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


def SL_S_PDR_Plot2(itercontrol,sender,origin,step_sim,steps_sim,SD_min_energy,SD_max_energy,Q_prod,Q_prod_steam,SD_energy,T_in_K,T_out_K,T_SD_K,plotPath,imageQlty,**kwargs):
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
    if itercontrol=='paso_10min':
        ax1.set_xlabel('Simulación: pasos diezminutales')
    elif itercontrol=='paso_15min':
        ax1.set_xlabel('Simulación: pasos quinceminutales')
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

    if origin==-2 or origin == -3 or origin == 1:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if origin==-1:
        fig.savefig(str(plotPath)+'flowrates.png', format='png', dpi=imageQlty)