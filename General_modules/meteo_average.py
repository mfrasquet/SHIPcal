# -*- coding: utf-8 -*-
"""
Created on Mon May 15 17:51:36 2017

@author: miguel
Script para obtener días típicos de la radiación solar mensualmente
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

#Localizacion
file_loc="/home/miguel/Desktop/Python_files/PLAT_VIRT/fresnel/METEO/Ouarzazate.dat"
file_loc2="/home/miguel/Desktop/Python_files/PLAT_VIRT/fresnel/METEO/Alicante_avg.dat"

#Archivo de meteo
meteo = pd.read_csv(file_loc, sep='\t', names = ["month", "day_month", "hour_day", "day_year","Gobal","Humidity","wind_vel","wind_dir","DNI","temp"])

radiation=meteo['DNI'].sum()/1000

def char_day_year(meteo):
    #Creacion de días característicos
    media=np.zeros((13,25))
    for m in range(1,13):
        for h in range(1,25):
            DNI= meteo .ix[(meteo ['month']==m) & (meteo ['hour_day'] == h)]
            media[m,h]=DNI['DNI'].mean()
    return media

#Genero una matriz con años característicos
media=char_day_year(meteo)



def year_form_char(media,meteo):
    dias_mes=[31,28,31,30,31,30,31,31,30,31,30,31]
    
    DNI_anual=np.zeros(8760)
    sim_step=np.zeros(8760)
    h_year=0
    for m in range(0,12):
        for d in range(0,dias_mes[m]):
            for h in range(0,24):
                DNI_anual[h_year]=np.round(media[m+1,h+1],2)
                sim_step[h_year]=h_year
                h_year=h_year+1

    DNI_anual=pd.DataFrame(DNI_anual)
    
    meteo['DNI']=DNI_anual    
    
    return meteo

#Creación de un año tipo con días característicos
#meteo=year_form_char(media,meteo)

#radiation2=meteo['DNI'].sum()/1000

#meteo.to_csv(file_loc2, sep='\t',index=False,header=False)



#Comparación TMY

meteoDB = pd.read_csv("/home/miguel/Desktop/Python_files/PLAT_VIRT/fresnel/METEO/meteoDB.csv", sep=',', header=None, names = ["Provincia", "Ciudad", "ressspi", "meteoFile","DNI","Latitud","Long","Huso"])
#meteoDB=meteoDB.iloc[1:]
#meteoDB =meteoDB.fillna(0)
mes=2
mes_word=["--","Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
for i in range(1,len(meteoDB.index)):
    if i==53:
        df=4
    if meteoDB["meteoFile"][i]!="0":
        file_loc="/home/miguel/Desktop/Python_files/PLAT_VIRT/fresnel/METEO/"
        file=file_loc+meteoDB["meteoFile"][i]
        meteo = pd.read_csv(file, sep='\t', names = ["month", "day_month", "hour_day", "day_year","Gobal","Humidity","wind_vel","wind_dir","DNI","temp"])
        media=char_day_year(meteo)
        plt.plot(media[mes],label=meteoDB["meteoFile"][i]+"="+str(np.int(np.sum(meteo['DNI'])/1000)))
        meteoDB["DNI"][i]=np.int(np.sum(meteo['DNI'])/1000)
        plt.suptitle(mes_word[mes], fontsize=14, fontweight='bold')
        plt.legend(bbox_to_anchor=(0.7, -0.2), loc=3, borderaxespad=0.)
    
plt.show()
meteoDB.to_csv("/home/miguel/Desktop/Python_files/PLAT_VIRT/fresnel/METEO/meteoDB.csv", sep=',',header=False)

