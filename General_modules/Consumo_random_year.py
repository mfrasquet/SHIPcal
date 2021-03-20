# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 11:11:40 2016

@author: miguel
"""
import sys

sys.path.append('/home/miguel/Desktop/Python_files/PLAT_VIRT/fresnel/modules/DataBase_modules')
sys.path.append('/home/miguel/Desktop/Python_files/PLAT_VIRT/fresnel/modules/Solatom_modules')
sys.path.append('/home/miguel/Desktop/Python_files/PLAT_VIRT/PV_PM_publico/modules/Solar_modules')
sys.path.append('/home/miguel/Desktop/Python_files/PLAT_VIRT/PV_PM_publico/modules/General_modules')
sys.path.append('/home/miguel/Desktop/Python_files/PLAT_VIRT/PV_PM_publico')

import random
from Conexion_DB import conexion_DB

id_USER=1

Consumption_design=.26
cnx = cnx=conexion_DB()    
mycursor=cnx.cursor()

for id_Hour in range(1,8760+1):
    Consumo=Consumption_design+.22*random.random()    
    mycursor.execute("UPDATE PERFORMANCE_"+str(id_USER)+" SET `Produccion`='"+str(Consumo)+"' where id_hour like "+ str(id_Hour)+";")

cnx.commit()
cnx.close()
