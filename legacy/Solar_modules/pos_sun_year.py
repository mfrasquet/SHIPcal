# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 11:00:15 2016
Funcion para el cáculo de la posición solar a lo largo del todo el año

@author: miguel
"""

from EQSolares import SolarEQ_simple
from EQSolares import theta_IAMs
from Conexion_DB import conexion_DB

# INPUTS DE LA TABLA DE USUARIO ----------------------------------------
#id_USER=2
#Lat=37
#Huso=0
#
## Colletor orientation parameters
#beta_rad=0 #Inclinacion respecto el terreno horizontal
#orient_az_rad=0 #Orientación del eje del colector respecto el Norte
# ----------------------------------------------------------------------

def pos_sun_year(Lat,Huso,beta_rad,orient_az_rad,id_USER):

    mysql_save=0
    #Inicializacón listas
    Month_y=[]
    Day_y=[]
    Day_yy=[]
    Hour_y=[]
    Hour_yy=[]
    W_y=[]
    SUN_ELV_y=[]
    SUN_AZ_y=[]
    SUN_ZEN_y=[]
    theta_transv_rad_y=[]
    theta_i_rad_y=[]
    
    # Call to solar EQ for each hour in the year
    
    Day_month=[32,29,32,31,32,31,32,32,31,32,31,32] #Xq en el range no se pilla el último valor
    
    day_year=1
    hour_year=1
    for Month in range(1,13):
        for Day in range(1,Day_month[Month-1]): # -1 xq el array empieza por 0
            for Hour in range(1,25):
                
                Month_y.append(Month)
                Day_y.append(Day)
                Day_yy.append(day_year)
                Hour_yy.append(hour_year)
                Hour_y.append(Hour)
                
                [W,SUN_ELV,SUN_AZ,DECL,SUN_ZEN]=SolarEQ_simple(Month,Day,Hour,Lat,Huso)
                W_y.append(W)
                SUN_ELV_y.append(SUN_ELV) 
                SUN_AZ_y.append(SUN_AZ) 
                SUN_ZEN_y.append(SUN_ZEN)
                
                # (5) Call function to calculate theta_transv & theta_inc
                [theta_transv_rad,theta_i_rad]=theta_IAMs(SUN_AZ,SUN_ELV,beta_rad,orient_az_rad)
                theta_transv_rad_y.append(abs(theta_transv_rad)) #Valor absoluto del theta_transv. Me da igual en que cuadrante esté, lo importante es el valor absoluto del ángulo
                theta_i_rad_y.append(theta_i_rad)
                
                hour_year=hour_year+1
            day_year=day_year+1
            
    if mysql_save==0: #Lo grabo en la tabla SOL_YEAR_*  en mySQL                
        cnx=conexion_DB()
        mycursor=cnx.cursor()
        
        for i in range(1,8760+1):
            mycursor.execute("UPDATE SOL_YEAR_"+str(id_USER)+" SET `Theta_i_rad`='"+str(theta_i_rad_y[i-1])+"' where id_Hour like "+ str(i)+";")
            mycursor.execute("UPDATE SOL_YEAR_"+str(id_USER)+" SET `Theta_transv_rad`='"+str(theta_transv_rad_y[i-1])+"' where id_Hour like "+ str(i)+";")
        
        cnx.commit()
        cnx.close()

    return [Month_y,Day_y,Day_yy,Hour_y,Hour_yy,SUN_ELV_y,SUN_AZ_y,theta_transv_rad_y,theta_i_rad_y]           
 
#[Month_y,Day_y,Day_yy,Hour_y,Hour_yy,SUN_ELV_y,SUN_AZ_y,theta_transv_rad_y,theta_i_rad_y]=pos_sun_year(Lat,Huso,beta_rad,orient_az_rad,id_USER)



