#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  7 16:00:27 2020

@author: jaarpa
"""
import numpy as np

test_array=np.array([1,2,34,5])

from SHIPcal import SHIPcal

from sliced_SHIPcal import SHIPcal_prep, SHIPcal_integration, SHIPcal_auto


def print_results(integration,fluid,plotVars,s_plotVars): #Function to compare the results
    #3 valores a comparar plotVars['Production_max'] (float) , plotVars['Production_lim'] (float), plotVars['Q_charg'] (list)

    #Check for Production_max
    production_max_diff = round(s_plotVars['Production_max'],2) - round(plotVars['Production_max'],2)

    #Check for Production_lim
    production_lim_diff = round(s_plotVars['Production_lim'],2) - round(plotVars['Production_lim'],2)

    #Check for sum(Q_charg)
    Q_charg_diff = round(sum(s_plotVars['Q_charg']),2) - round(sum(plotVars['Q_charg']),2)

    print("Difference sliced-traditional in the {} integration with {} fluid is".format(integration, fluid))
    
    print("{} in the production_max".format(production_max_diff))
    
    print("{} in the production_lim_diff".format(production_lim_diff))
    
    print("{} in the Q_charg_diff".format(Q_charg_diff))
    
    return production_max_diff,production_lim_diff,Q_charg_diff


######################################### Simulation parameters taken from the bottom of the SHIPcal.py #########################################

imageQlty=200

plots=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] 

finance_study=1

month_ini_sim=1
day_ini_sim=1
hour_ini_sim=1

month_fin_sim=12
day_fin_sim=31
hour_fin_sim=24

mofINV=1 #Sobre el coste de inversion
mofDNI=1  #Corrección a fichero Meteonorm
mofProd=1 #Factor de seguridad a la producción de los módulos

num_loops=1
n_coll_loop=8
almVolumen=10000 #litros

type_integration="SL_S_PDS" #To be iterated

# --------------------------------------------------
confReport={'lang':'spa','sender':'alguien','cabecera':'Resultados de la <br> simulación','mapama':0}
modificators={'mofINV':mofINV,'mofDNI':mofDNI,'mofProd':mofProd}
desginDict={'num_loops':num_loops,'n_coll_loop':n_coll_loop,'type_integration':type_integration,'almVolumen':almVolumen}
simControl={'finance_study':finance_study,'mes_ini_sim':month_ini_sim,'dia_ini_sim':day_ini_sim,'hora_ini_sim':hour_ini_sim,'mes_fin_sim':month_fin_sim,'dia_fin_sim':day_fin_sim,'hora_fin_sim':hour_fin_sim}
# ---------------------------------------------------

origin=1 #As called from an external fornt-end

#To perform simulations from command line using hardcoded inputs
inputsDjango={'pressureUnit':'bar',
              'pressure':5,
              'demand':1875*8760,
              'demandUnit':'kWh',
              'hourEND':24,
              'hourINI':1,
              'Jan':1/12,
              'Feb':1/12,
              'Mar':1/12,
              'Apr':1/12,
              'May':1/12,
              'Jun':1/12,
              'Jul':1/12,
              'Aug':1/12,
              'Sep':1/12,
              'Oct':1/12,
              'Nov':1/12,
              'Dec':1/12,
              'Mond':0.143,
              'Tues':0.143,
              'Wend':0.143,
              'Thur':0.143,
              'Fri':0.143,
              'Sat':0.143,
              'Sun':0.143,
              'date':'2020-05-08',
              'name':'jaarpa',
              'industry':'comparison_test',
              'email':'jaarpa97@gmail.com',
              'sectorIndustry':'developing',
              'fuel':'Gasoil-B',
              'fuelPrice':0.05,
              'co2TonPrice':0,
              'co2factor':1,
              'fuelUnit':'kWh',
              'businessModel':'turnkey',
              'location':'Bakersfield',
              'location_aux':'',
              'surface':None,
              'terrain':'',
              'orientation':'NS',
              'inclination':'flat',
              'shadows':'free',
              'distance':None,
              'process':'',
              'fluid':'water',
              'connection':'',
              'tempOUT':65,
              'tempIN':20,
             }

last_reg=666

#################################################################################################################################################

print("Running...")

#Preparing for liquid phase integrations

o_version, initial_variables_dict, coll_par, integration_Dict = SHIPcal_prep(origin,inputsDjango,confReport,modificators,simControl)

for integration in ['SL_L_P', 'SL_L_PS', 'SL_L_RF', 'SL_L_S', 'SL_L_S_PH']:#Tests for liquid phase integrations #Checked 'SL_L_P', 'SL_L_PS', 'SL_L_RF', 
    
    desginDict.update({'type_integration':integration})

    [jSonResults,plotVars,reportsVar,version]=SHIPcal(origin,inputsDjango,plots,imageQlty,confReport,modificators,desginDict,simControl,last_reg)
    
    
    initial_variables_dict = SHIPcal_integration(desginDict,initial_variables_dict,integration_Dict) #This second section of SHIPcal updates the integration variables depending on the type of integrations. This will be used mainly to iterate over the storage capacity.
    #ref_initial_variables_dict=initial_variables_dict.copy()
    #coll_par.update({'auto':'on'})
    #LCOE = SHIPcal_auto(origin,inputsDjango,plots,imageQlty,confReport,desginDict,initial_variables_dict,coll_par,modificators,last_reg)
    #print(LCOE)
    coll_par.update({'auto':'off'})

    [s_jSonResults,s_plotVars,s_reportsVar,o_version] = SHIPcal_auto(origin,inputsDjango,plots,imageQlty,confReport,desginDict,initial_variables_dict,coll_par,modificators,last_reg)

    print_results(integration,inputsDjango['fluid'],plotVars,s_plotVars)

    # for key in initial_variables_dict.keys():
    #     if type(initial_variables_dict[key]) == type(test_array) and type(ref_initial_variables_dict[key]) == type(test_array):
    #         if not np.array_equal(initial_variables_dict[key],ref_initial_variables_dict[key]):
    #             print("Hay un cambio en {}".format(key))
    #     else:
    #         if initial_variables_dict[key] != ref_initial_variables_dict[key]:
    #             print("Hay un cambio en {}".format(key))

#Preparing for steam phase integrations

inputsDjango.update({'fluid':'steam','tempOUT':235,'tempIN':20, 'pressure':30})

desginDict.update({'num_loops':5,'n_coll_loop':24})

o_version, initial_variables_dict, coll_par, integration_Dict = SHIPcal_prep(origin,inputsDjango,confReport,modificators,simControl)

for integration in ['SL_S_FW','SL_S_FWS','SL_S_PD_OT','PL_E_PM','SL_S_MW','SL_S_MWS','SL_S_PD','SL_S_PDS']: #Tests for steam phase integrations
    
    desginDict.update({'type_integration':integration})
    
    [jSonResults,plotVars,reportsVar,version]=SHIPcal(origin,inputsDjango,plots,imageQlty,confReport,modificators,desginDict,simControl,last_reg)
        
    initial_variables_dict = SHIPcal_integration(desginDict,initial_variables_dict, integration_Dict) #This second section of SHIPcal updates the integration variables depending on the type of integrations. This will be used mainly to iterate over the storage capacity.
    #coll_par.update({'auto':'on'})
    #LCOE = SHIPcal_auto(origin,inputsDjango,plots,imageQlty,confReport,desginDict,initial_variables_dict,coll_par,modificators,last_reg)
    #print(LCOE)
    coll_par.update({'auto':'off'})

    [s_jSonResults,s_plotVars,s_reportsVar,o_version] = SHIPcal_auto(origin,inputsDjango,plots,imageQlty,confReport,desginDict,initial_variables_dict,coll_par,modificators,last_reg)
    
    print_results(integration,inputsDjango['fluid'],plotVars,s_plotVars)
    

