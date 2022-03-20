#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 17:27:44 2020

@author: miguel
"""

#from SHIPcal import SHIPcal
from sliced_SHIPcal import SHIPcal_prep,SHIPcal_integration,SHIPcal_auto

"""
    #--> Integration parameters
    
    lim_inf_DNI=200 # Minimum temperature to start production [W/m²]
    m_dot_min_kgs=0.06 # Minimum flowrate before re-circulation [kg/s]
    coef_flow_rec=1 # Multiplier for flowrate when recirculating [-]
    Boiler_eff=0.8 # Boiler efficiency to take into account the excess of fuel consumed [-]
    subcooling=5 #Deegre of subcooling
    
        ## SL_L_RF
    heatFactor=.9 # Percentage of temperature variation (T_out - T_in) provided by the heat exchanger (for design) 
    HX_eff=0.9 # Simplification for HX efficiency
    DELTA_ST=30 # Temperature delta over the design process temp for the storage
    
    ## SL_L_S_PH & SL_L_RF
    DELTA_HX=5 # Degrees for temperature delta experienced in the heat exchanger (for design) 

"""

errorList=[]

last_reg='666'

finance_study=1

      
origin=-2
sender='solatom'
confReport={'lang':'spa','sender':sender,'cabecera':'Resultados de la <br> simulación','mapama':0}

month_ini_sim=6
day_ini_sim=21
hour_ini_sim=1

month_fin_sim=6
day_fin_sim=22
hour_fin_sim=24

simControl={'finance_study':finance_study,'mes_ini_sim':month_ini_sim,'dia_ini_sim':day_ini_sim,'hora_ini_sim':hour_ini_sim,'mes_fin_sim':month_fin_sim,'dia_fin_sim':day_fin_sim,'hora_fin_sim':hour_fin_sim}    

# -------------------- FINE TUNNING CONTROL ---------
mofINV=1 #Sobre el coste de inversion
mofDNI=1  #Corrección a fichero Meteonorm
mofProd=1 #Factor de seguridad a la producción de los módulos

modificators={'mofINV':mofINV,'mofDNI':mofDNI,'mofProd':mofProd}

def print_results(integration,fluid,plotVars,max_ref,lim_ref,Q_charg=1):
    error=''
    if integration in ['SL_L_PS','SL_L_S','SL_L_S_PH','SL_S_FWS']:
        aux='v1.1.10 Test #'+integration+'-'+fluid+':\n Q_prod:'+str(round(plotVars['Production_max'],2))+' kWh  -> Error:'+str(100*round(1-plotVars['Production_max']/max_ref,3))+'%\n Q_prod_lim:'+str(round(plotVars['Production_lim'],2))+' kWh  ->Error:'+str(100*round(1-plotVars['Production_lim']/lim_ref,3))+'%\n Q_charg:'+str(round(sum(plotVars['Q_charg']),2))+' kWh  ->Error:'+str(100*round(1-sum(plotVars['Q_charg'])/Q_charg,3))+'%\n'
        if not 0.98< plotVars['Production_max']/max_ref <=1.1 or not 0.98< plotVars['Production_lim']/lim_ref <=1.1 or  not 0.98< sum(plotVars['Q_charg'])/Q_charg <=1.1:
            error=integration+'-'+fluid
    else:
        aux='v1.1.10 Test #'+integration+'-'+fluid+':\n Q_prod:'+str(round(plotVars['Production_max'],2))+' kWh  -> Error:'+str(100*round(1-plotVars['Production_max']/max_ref,3))+'%\n Q_prod_lim:'+str(round(plotVars['Production_lim'],2))+' kWh  ->Error:'+str(100*round(1-plotVars['Production_lim']/lim_ref,3))+'%\n'
        if not 0.98< plotVars['Production_max']/max_ref <=1.1 or not 0.98< plotVars['Production_lim']/lim_ref <=1.1:
            error=integration+'-'+fluid

    
    return error,aux


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#Test "Molten Salts"
print("TESTS MOLTEN SALT ##############################################")
solutions={'SL_L_P':[10347.885461205757,10126.182549222665,0],
           'SL_L_PS':[10347.885461205757,10347.885461205757,221.70291198309258],
           'SL_L_S':[9958.026061138959,9109.880939227516,707.199286276984],
           'SL_L_S_PH':[10725.522847905004,10725.522847905004,419.95257932664344],
           'SL_L_RF':[9335.52595897536,9131.12444703713,0]}


"""
heatFactor=.9 # Percentage of temperature variation (T_out - T_in) provided by the heat exchanger (for design) 
HX_eff=0.9 # Simplification for HX efficiency
DELTA_ST=30 # Temperature delta over the design process temp for the storage

"""

tempIN=290
tempOUT=360
pressure=6
demand=900*8760
fluid='moltenSalt'

almVolumen=10000    
num_loops=8;n_coll_loop=8

inputsDjango= {'date': '2020-03-23', 'name': 'miguel', 'email': 'miguel.frasquet@solatom.com', 'industry': 'prueba2', 'sectorIndustry': 'Chemical', 'fuel': 'NG', 'fuelPrice': 0.05, 'co2TonPrice': 0.0, 'co2factor': 0.0002, 'fuelUnit': 'eur_kWh', 'businessModel': 'turnkey', 'location': 'Bakersfield', 'location_aux': '', 'surface': None, 'terrain': '', 'distance': None, 'orientation': 'NS', 'inclination': 'flat', 'shadows': 'free', 'fluid': fluid, 'pressure': pressure, 'pressureUnit': 'bar', 'tempIN': tempIN, 'tempOUT': tempOUT, 'connection': '', 'process': '', 'demand': demand, 'demandUnit': 'kWh', 'hourINI': 1, 'hourEND': 24, 'Mond': 0.143, 'Tues': 0.143, 'Wend': 0.143, 'Thur': 0.143, 'Fri': 0.143, 'Sat': 0.143, 'Sun': 0.143, 'Jan': 0.08333333333333333, 'Feb': 0.08333333333333333, 'Mar': 0.08333333333333333, 'Apr': 0.08333333333333333, 'May': 0.08333333333333333, 'Jun': 0.08333333333333333, 'Jul': 0.08333333333333333, 'Aug': 0.08333333333333333, 'Sep': 0.08333333333333333, 'Oct': 0.08333333333333333, 'Nov': 0.08333333333333333, 'Dec': 0.08333333333333333, 'last_reg': 711}

version, initial_variables_dict, coll_par, integration_Dict = SHIPcal_prep(origin,inputsDjango,confReport,modificators,simControl)
coll_par.update({'auto':'off'})

for type_integration in ["SL_L_P","SL_L_PS","SL_L_S","SL_L_S_PH","SL_L_RF"]:
    
    desginDict={'num_loops':num_loops,'n_coll_loop':n_coll_loop,'type_integration':type_integration,'almVolumen':almVolumen}
    
    initial_variables_dict = SHIPcal_integration(desginDict,initial_variables_dict, integration_Dict)
    [template_vars,plotVars,reportsVar,version] = SHIPcal_auto(origin,inputsDjango,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],200,confReport,desginDict,initial_variables_dict,coll_par,modificators,666)
    
    #[template_vars,plotVars,reportsVar,version]=SHIPcal(origin,inputsDjango,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],200,confReport,modificators,desginDict,simControl,666)
    [error,aux]=print_results(type_integration,fluid,plotVars,solutions[type_integration][0],solutions[type_integration][1],solutions[type_integration][2])
    print(aux)
    errorList.append(error)


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#Tests "Oil" Similar to the PhD thesis examples
print("TESTS THERMAL OIL ##############################################")
      
      
solutions={'SL_L_P':[11038.077926364267,10629.74316306723,0],
           'SL_L_PS':[11038.077926364267,11038.077926364267,408.33476329703694],
           'SL_L_S':[10755.940333589375,9568.775701023602,749.4188951198007],
           'SL_L_S_PH':[11726.960067406026,11726.960067406026,694.03351372886],
           'SL_L_RF':[9986.476875069558,9604.425114008944,0]}

    
"""
heatFactor=.9 # Percentage of temperature variation (T_out - T_in) provided by the heat exchanger (for design) 
HX_eff=0.9 # Simplification for HX efficiency
DELTA_ST=30 # Temperature delta over the design process temp for the storage

"""

tempIN=180
tempOUT=290
pressure=6
demand=900*8760
fluid='oil'

almVolumen=10000
num_loops=8;n_coll_loop=8

inputsDjango= {'date': '2020-03-23', 'name': 'miguel', 'email': 'miguel.frasquet@solatom.com', 'industry': 'prueba2', 'sectorIndustry': 'Chemical', 'fuel': 'NG', 'fuelPrice': 0.05, 'co2TonPrice': 0.0, 'co2factor': 0.0002, 'fuelUnit': 'eur_kWh', 'businessModel': 'turnkey', 'location': 'Bakersfield', 'location_aux': '', 'surface': None, 'terrain': '', 'distance': None, 'orientation': 'NS', 'inclination': 'flat', 'shadows': 'free', 'fluid': fluid, 'pressure': pressure, 'pressureUnit': 'bar', 'tempIN': tempIN, 'tempOUT': tempOUT, 'connection': '', 'process': '', 'demand': demand, 'demandUnit': 'kWh', 'hourINI': 1, 'hourEND': 24, 'Mond': 0.143, 'Tues': 0.143, 'Wend': 0.143, 'Thur': 0.143, 'Fri': 0.143, 'Sat': 0.143, 'Sun': 0.143, 'Jan': 0.08333333333333333, 'Feb': 0.08333333333333333, 'Mar': 0.08333333333333333, 'Apr': 0.08333333333333333, 'May': 0.08333333333333333, 'Jun': 0.08333333333333333, 'Jul': 0.08333333333333333, 'Aug': 0.08333333333333333, 'Sep': 0.08333333333333333, 'Oct': 0.08333333333333333, 'Nov': 0.08333333333333333, 'Dec': 0.08333333333333333, 'last_reg': 711}

version, initial_variables_dict, coll_par, integration_Dict = SHIPcal_prep(origin,inputsDjango,confReport,modificators,simControl)
coll_par.update({'auto':'off'})

for type_integration in ["SL_L_P","SL_L_PS","SL_L_S","SL_L_S_PH","SL_L_RF"]:
        
    desginDict={'num_loops':num_loops,'n_coll_loop':n_coll_loop,'type_integration':type_integration,'almVolumen':almVolumen}
    
    initial_variables_dict = SHIPcal_integration(desginDict,initial_variables_dict, integration_Dict)
    [template_vars,plotVars,reportsVar,version] = SHIPcal_auto(origin,inputsDjango,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],200,confReport,desginDict,initial_variables_dict,coll_par,modificators,666)
    
    #[template_vars,plotVars,reportsVar,version]=SHIPcal(origin,inputsDjango,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],200,confReport,modificators,desginDict,simControl,666)
    [error,aux]=print_results(type_integration,fluid,plotVars,solutions[type_integration][0],solutions[type_integration][1],solutions[type_integration][2])
    print(aux)
    errorList.append(error)
    
    
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#Tests "Water" 
print("TESTS WATER ##############################################")
      
      
solutions={'SL_L_P':[12437.409006259013,11650.137743509606,0],
           'SL_L_PS':[12437.409006259013,12097.140133288745,447.00238977913983],
           'SL_L_S':[12313.304259772056,11297.333445216915,660.2661892418289],
           'SL_L_S_PH':[12466.725547412885,12047.492760667106,564.5184178770427],
           'SL_L_RF':[11187.868164159638,10481.50226307402,0]}

"""
heatFactor=.9 # Percentage of temperature variation (T_out - T_in) provided by the heat exchanger (for design) 
HX_eff=0.9 # Simplification for HX efficiency
DELTA_ST=30 # Temperature delta over the design process temp for the storage

"""

tempIN=90
tempOUT=130
pressure=6
demand=900*8760
fluid='water'

almVolumen=10000
num_loops=8;n_coll_loop=8

inputsDjango= {'date': '2020-03-23', 'name': 'miguel', 'email': 'miguel.frasquet@solatom.com', 'industry': 'prueba2', 'sectorIndustry': 'Chemical', 'fuel': 'NG', 'fuelPrice': 0.05, 'co2TonPrice': 0.0, 'co2factor': 0.0002, 'fuelUnit': 'eur_kWh', 'businessModel': 'turnkey', 'location': 'Bakersfield', 'location_aux': '', 'surface': None, 'terrain': '', 'distance': None, 'orientation': 'NS', 'inclination': 'flat', 'shadows': 'free', 'fluid': fluid, 'pressure': pressure, 'pressureUnit': 'bar', 'tempIN': tempIN, 'tempOUT': tempOUT, 'connection': '', 'process': '', 'demand': demand, 'demandUnit': 'kWh', 'hourINI': 1, 'hourEND': 24, 'Mond': 0.143, 'Tues': 0.143, 'Wend': 0.143, 'Thur': 0.143, 'Fri': 0.143, 'Sat': 0.143, 'Sun': 0.143, 'Jan': 0.08333333333333333, 'Feb': 0.08333333333333333, 'Mar': 0.08333333333333333, 'Apr': 0.08333333333333333, 'May': 0.08333333333333333, 'Jun': 0.08333333333333333, 'Jul': 0.08333333333333333, 'Aug': 0.08333333333333333, 'Sep': 0.08333333333333333, 'Oct': 0.08333333333333333, 'Nov': 0.08333333333333333, 'Dec': 0.08333333333333333, 'last_reg': 711}

version, initial_variables_dict, coll_par, integration_Dict = SHIPcal_prep(origin,inputsDjango,confReport,modificators,simControl)
coll_par.update({'auto':'off'})

for type_integration in ["SL_L_P","SL_L_PS","SL_L_S","SL_L_S_PH","SL_L_RF"]:
    
    desginDict={'num_loops':num_loops,'n_coll_loop':n_coll_loop,'type_integration':type_integration,'almVolumen':almVolumen}
    
    initial_variables_dict = SHIPcal_integration(desginDict,initial_variables_dict, integration_Dict)
    [template_vars,plotVars,reportsVar,version] = SHIPcal_auto(origin,inputsDjango,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],200,confReport,desginDict,initial_variables_dict,coll_par,modificators,666)
    
    #[template_vars,plotVars,reportsVar,version]=SHIPcal(origin,inputsDjango,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],200,confReport,modificators,desginDict,simControl,666)
    [error,aux]=print_results(type_integration,fluid,plotVars,solutions[type_integration][0],solutions[type_integration][1],solutions[type_integration][2])
    print(aux)
    errorList.append(error)
    

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#Tests "Steam" 
print("TESTS STEAM ##############################################")
      
      
solutions={'SL_S_PD':[19957.777876359476,19665.50597226274,0],
           'SL_S_FW':[22145.85714253118,11546.902770833289,0],
           'SL_S_FWS':[22089.768050991108,15340.178857124336,3804.0030331414673],
           }

    
"""
heatFactor=.9 # Percentage of temperature variation (T_out - T_in) provided by the heat exchanger (for design) 
HX_eff=0.9 # Simplification for HX efficiency
DELTA_ST=30 # Temperature delta over the design process temp for the storage

"""

tempIN=20
tempOUT=235
pressure=30
demand=1875*8760
fluid='steam'

almVolumen=10000
num_loops=5;n_coll_loop=24

inputsDjango= {'date': '2020-03-23', 'name': 'miguel', 'email': 'miguel.frasquet@solatom.com', 'industry': 'prueba2', 'sectorIndustry': 'Chemical', 'fuel': 'NG', 'fuelPrice': 0.05, 'co2TonPrice': 0.0, 'co2factor': 0.0002, 'fuelUnit': 'eur_kWh', 'businessModel': 'turnkey', 'location': 'Bakersfield', 'location_aux': '', 'surface': None, 'terrain': '', 'distance': None, 'orientation': 'NS', 'inclination': 'flat', 'shadows': 'free', 'fluid': fluid, 'pressure': pressure, 'pressureUnit': 'bar', 'tempIN': tempIN, 'tempOUT': tempOUT, 'connection': '', 'process': '', 'demand': demand, 'demandUnit': 'kWh', 'hourINI': 1, 'hourEND': 24, 'Mond': 0.143, 'Tues': 0.143, 'Wend': 0.143, 'Thur': 0.143, 'Fri': 0.143, 'Sat': 0.143, 'Sun': 0.143, 'Jan': 0.08333333333333333, 'Feb': 0.08333333333333333, 'Mar': 0.08333333333333333, 'Apr': 0.08333333333333333, 'May': 0.08333333333333333, 'Jun': 0.08333333333333333, 'Jul': 0.08333333333333333, 'Aug': 0.08333333333333333, 'Sep': 0.08333333333333333, 'Oct': 0.08333333333333333, 'Nov': 0.08333333333333333, 'Dec': 0.08333333333333333, 'last_reg': 711}

version, initial_variables_dict, coll_par, integration_Dict = SHIPcal_prep(origin,inputsDjango,confReport,modificators,simControl)
coll_par.update({'auto':'off'})

for type_integration in ["SL_S_PD","SL_S_FW",'SL_S_FWS']:
    
    desginDict={'num_loops':num_loops,'n_coll_loop':n_coll_loop,'type_integration':type_integration,'almVolumen':almVolumen}
    
    initial_variables_dict = SHIPcal_integration(desginDict,initial_variables_dict, integration_Dict)
    [template_vars,plotVars,reportsVar,version] = SHIPcal_auto(origin,inputsDjango,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],200,confReport,desginDict,initial_variables_dict,coll_par,modificators,666)
    
    #[template_vars,plotVars,reportsVar,version]=SHIPcal(origin,inputsDjango,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],200,confReport,modificators,desginDict,simControl,666)
    [error,aux]=print_results(type_integration,fluid,plotVars,solutions[type_integration][0],solutions[type_integration][1],solutions[type_integration][2])
    print(aux)
    errorList.append(error)


print('Errors found: ',errorList)
