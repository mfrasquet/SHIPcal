#Function to calculate the Solar position (Sun Elevation and Azimuth)
#This function uses a very simple method
#Miguel Frasquet
#Juan Martinez
import numpy as np
#from matplotlib import pyplot as plt
from General_modules.func_General import calc_hour_year
import os

def SolarEQ_simple (Month,Day,Hour,Lat,Huso): #Returns the hour angle (W) [rad], sun elevation angle[rad], azimuth angle[rad], declination [rad] and zenithal angle [rad] of the sun for each the specified hour, latitude[°], anf time zone given in the inputs.

    gr=np.pi/180; #Just to convert RAD-DEG 
    
    #Read the Juilan day file and save it in a matrix
    JUL_DAY=np.loadtxt(os.path.dirname(os.path.dirname(__file__))+'/Solar_modules/Julian_day_prueba.txt',delimiter='\t');
  
    
    #Calculates the Julian Day
    Jul_day=JUL_DAY[int(Day-1),int(Month-1)];
    
    #Declination
    
    DJ=2*np.pi/365*(Jul_day-1); #Julian day in rad
    DECL=(0.006918-0.399912*np.cos(DJ)+ 0.070257*np.sin(DJ)-0.006758*np.cos(2*DJ)+0.000907*np.sin(2*DJ)-0.002697*np.cos(3*DJ)+0.00148*np.sin(3*DJ));
    DECL_deg=DECL/gr;
    
    #Hour
    W_deg=(Hour-12-Huso)*15;
    W=W_deg*gr;
    
    #Sun elevation
    XLat=Lat*gr;
    sin_Elv=np.sin(DECL)*np.sin(XLat)+np.cos(DECL)*np.cos(XLat)*np.cos(W);
    SUN_ELV=np.arcsin(sin_Elv);
    SUN_ELV_deg=SUN_ELV/gr;
    
    SUN_ZEN=(np.pi/2)-SUN_ELV;
    #Sun azimuth
    SUN_AZ=np.arcsin(np.cos(DECL)*np.sin(W)/np.cos(SUN_ELV));
    
    verif=(np.tan(DECL)/np.tan(XLat));
    if np.cos(W)>=verif:
        SUN_AZ=SUN_AZ;  
    else:
            if SUN_AZ >0:
                SUN_AZ=((np.pi/2)+((np.pi/2)-abs(SUN_AZ)));
            else:
                SUN_AZ=-((np.pi/2)+((np.pi/2)-abs(SUN_AZ)));
    
    
    
#    SUN_AZ_deg=SUN_AZ/gr;
#    a=[W,SUN_ELV,SUN_AZ,DECL,SUN_ZEN]
       
    return [W,SUN_ELV,SUN_AZ,DECL,SUN_ZEN]
    
def theta_IAMs(SUN_AZ_DP,SUN_ELV_DP,beta,orient_az_rad):
    #INPUTS
    #beta=0 #Inclinacion respecto el terreno horizontal
    #orient_az_rad=0 #Orientación del eje del colector respecto el Norte
    
    
    #Correción del azimut para ajustarlo a las formulas
    #En EQSolares un azimut Sur=0 (origen Sur, hacia Este -, hacia West +) pero para estas formulas sería 180 (Oriegen Norte giro + agujas reloj)
    azimuth_solar_corr_rad=np.pi+SUN_AZ_DP
    
    # ANGULO DE INCIDENCIA -----------------------------------
    
    #En el caso de orientacion Norte-Sur
    #theta_i_rad=np.arccos(np.sqrt(1-(np.cos(SUN_ELV_DP)**2*np.cos(azimuth_solar_corr_rad)**2)))
    #theta_i_deg=theta_i_rad*180/np.pi
    
    #Caso general 

    theta_i_rad=np.arccos(np.sqrt(1-(np.cos(SUN_ELV_DP-beta)-np.cos(beta)*np.cos(SUN_ELV_DP)*(1-np.cos(azimuth_solar_corr_rad-orient_az_rad)))**2))
    theta_i_deg=theta_i_rad*180/np.pi
    # ------------------------------------------------------
    
    # ANGULO TRANSVERSAL
    
    #Caso general
    theta_transv_rad=np.arctan((np.cos(SUN_ELV_DP)*np.sin(azimuth_solar_corr_rad-orient_az_rad))/(np.sin(SUN_ELV_DP-beta)+np.sin(beta)*np.cos(SUN_ELV_DP)*(1-np.cos(azimuth_solar_corr_rad-orient_az_rad))))
    theta_transv_deg=theta_transv_rad*180/np.pi
    # -----------------------------------------------------
    return [theta_transv_deg,theta_i_deg]

def theta_IAMs_v2(SUN_AZ,SUN_ELV,LONG_INCL,HEAD,ROLL):
   
    
   sunX=np.cos(SUN_ELV)*np.sin(SUN_AZ)
   sunY=np.cos(SUN_ELV)*np.cos(SUN_AZ)
   sunZ=np.sin(SUN_ELV)

   theta=LONG_INCL*np.pi/180
   alpha=ROLL*np.pi/180
   beta=HEAD*np.pi/180

   sunXl = sunX*(np.cos(alpha)*np.cos(beta) + np.sin(alpha)*np.sin(beta)*np.sin(theta)) - sunY*(np.cos(alpha)*np.sin(beta) - np.cos(beta)*np.sin(alpha)*np.sin(theta)) + sunZ*np.sin(alpha)*np.cos(theta)
   sunYl = sunY*np.cos(beta)*np.cos(theta) - sunZ*np.sin(theta) + sunX*np.sin(beta)*np.cos(theta)
   sunZl = sunY*(np.sin(alpha)*np.sin(beta) + np.cos(alpha)*np.cos(beta)*np.sin(theta)) - sunX*(np.cos(beta)*np.sin(alpha) - np.cos(alpha)*np.sin(beta)*np.sin(theta)) + sunZ*np.cos(alpha)*np.cos(theta)



   elevacion_local_trans=np.arctan(sunZl/sunXl) #Where is the sun in an angle measured from south (0) to north (180)?

   if elevacion_local_trans<0 and sunZl>0:
       elevacion_local_trans=elevacion_local_trans+np.pi # adjuste arc tangente para tener elevaccion es siempre positiva

   if elevacion_local_trans>0 and sunZl<0:
       elevacion_local_trans=elevacion_local_trans-np.pi #elevaccion relativa negativa, en el (imposible?) caso que el sol sea por debajo del plano base del contenedor


   elevacion_local_long=np.arctan(sunZl/sunYl) #Where is the sun in an angle measured from east (0) to west (180)?

   if elevacion_local_long<0 and sunZl>0:
       elevacion_local_long=elevacion_local_long+np.pi #adjuste arc tangente para tener elevaccion es siempre positiva

   if elevacion_local_long>0 and sunZl<0:
       elevacion_local_long=elevacion_local_long-np.pi #elevaccion relativa negativa, en el (imposible?) caso que el sol sea por debajo del plano base del contenedor


   elevacion_local_long=elevacion_local_long*180/np.pi-90
   elevacion_local_trans=elevacion_local_trans*180/np.pi-90



   return[elevacion_local_trans,elevacion_local_long]
    
def IAM_calc(ang_target,IAM_type,file_loc):
    ang_target=abs(ang_target)
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

def Meteo_data (file_meteo,sender='notCIMAV', collector='plane'): #This function exports the TMY file to 'data', the DNI and temperature array of values for  each hour in the year from the file_meteo path to file
    #Only if the optional argument sender is received and is == 'CIMAV'
    if sender == 'CIMAV':
        data = np.loadtxt(file_meteo, delimiter="\t", skiprows=4) #Will read this format, since the first 4 rows has the place, location and headings data
        if collector=='concentrator':
            DNI=data[:,5]#If the collector is a concentrator type collector this variable will carry the DNI
        else:
            DNI=data[:,6]#But if it is not a concentrator tipe it will carry the global radiation
        temp=data[:,7]
    else:
        data = np.loadtxt(file_meteo, delimiter="\t")
        DNI=data[:,8]
        temp=data[:,9]
    return [data,DNI,temp]



    #INPUTS
#plot_Optics=1
#file_loc="/home/miguel/Desktop/Python_files/FRESNEL/METEO/Sevilla.dat"
##Localizacion
#Lat=37
#Huso=2
#
#mes_ini_sim=1
#dia_ini_sim=21
#hora_ini_sim=1
#
#mes_fin_sim=1
#dia_fin_sim=22
#hora_fin_sim=24
                                                                                                         #Sender is an optional argument, if not received continues normaly
def SolarData(file_loc,Lat,Huso,mes_ini_sim,dia_ini_sim,hora_ini_sim,mes_fin_sim,dia_fin_sim,hora_fin_sim,sender='notCIMAV'): #This function returns an "output" array with the month, day of the month, hour of the day, hour of the year hour angle,SUN_ELVevation, suN_AZimuth,DECLINATION, SUN_ZENITHAL, DNI,temp_sim,step_sim for every hour between the starting and ending hours in the year.  It also returns the starting and ending hour in the year.

    hour_year_ini=calc_hour_year(mes_ini_sim,dia_ini_sim,hora_ini_sim)#Calls a function within this same script yo calculate the corresponding hout in the year for the day/month/hour of start and end
    hour_year_fin=calc_hour_year(mes_fin_sim,dia_fin_sim,hora_fin_sim)
    
    if hour_year_ini <= hour_year_fin: #Checks that the starting hour is before than the enfing hour
        sim_steps=hour_year_fin-hour_year_ini #Stablishes the number of steps as the hours between the starting and ending hours
    else:
        raise ValueError('End time is smaller than start time') 
    
    
    #Llamada al archivo de meteo completo
    (data,DNI,temp)=Meteo_data(file_loc,sender)#Calls another function within this same script that reads the TMY.dat file 
    data=np.array(data) #Array where every row is an hour and the columns are month,day in the month, hour of the month, hour of the year, ..., DNI, Temp
    DNI=np.array(DNI) #Vector with DNI values for every hour in the year
    temp=np.array(temp) #Vector with the temperature for every hour in the year
    
    #Bucle de simulacion
    #Starts the vectors of sim_steps length to store date in them
    
    W_sim=np.zeros (sim_steps)
    SUN_ELV_sim=np.zeros (sim_steps)
    SUN_AZ_sim=np.zeros (sim_steps)
    DECL_sim=np.zeros (sim_steps)
    SUN_ZEN_sim=np.zeros (sim_steps)
    step_sim=np.zeros (sim_steps)
    DNI_sim=np.zeros (sim_steps)
    temp_sim=np.zeros (sim_steps)
    month_sim=np.zeros (sim_steps)
    day_sim=np.zeros (sim_steps)
    hour_sim=np.zeros (sim_steps)
    hour_year_sim=np.zeros (sim_steps)
    
    
    
    step=0
    for step in range(0,sim_steps):
        step_sim[step]=step
        
        month_sim[step]=data[hour_year_ini+step-1,0]
        day_sim[step]=data[hour_year_ini+step-1,1]
        hour_sim[step]=data[hour_year_ini+step-1,2]
        
        hour_year_sim[step]=hour_year_ini+step
    
        DNI_sim[step]=DNI[hour_year_ini+step-1]
        temp_sim[step]=temp[hour_year_ini+step-1]
    
        #Posicion solar
        W,SUN_ELV,SUN_AZ,DECL,SUN_ZEN=SolarEQ_simple (month_sim[step],day_sim[step] ,hour_sim[step],Lat,Huso) #calls another unction in within this script that calculates the solar positional angles for the specfied hour of the day and month
        W_sim[step]=W
        SUN_ELV_sim[step]=SUN_ELV   #rad
        SUN_AZ_sim[step]=SUN_AZ     #rad
        DECL_sim[step]=DECL         #rad
        SUN_ZEN_sim[step]=SUN_ZEN   #rad
     
        
        step+=1
    
    output=np.column_stack((month_sim,day_sim,hour_sim,hour_year_sim,W_sim,SUN_ELV_sim,SUN_AZ_sim,DECL_sim,SUN_ZEN_sim,DNI_sim,temp_sim,step_sim)) #Arranges the calculated data in a massive array with the previusly calculated vector as columns
        
#    if plot_Optics==1:    
#        fig = plt.figure(1)
#        fig.suptitle('Optics', fontsize=14, fontweight='bold')
#        ax1 = fig.add_subplot(111)  
#        ax1 .plot(step_sim, SUN_AZ_sim,'.b-',label="SUN_AZ")
#        ax1 .plot(step_sim, W_sim,'.g-',label="W")
#        ax1 .axhline(y=0,xmin=0,xmax=sim_steps,c="blue",linewidth=0.5,zorder=0)
#        ax1.set_xlabel('simulation')
#        ax1.set_ylabel('radians')
#        ax1 .plot(step_sim, SUN_ELV_sim,'.r-',label="SUN_ELV")
#        plt.legend(bbox_to_anchor=(1.15, 1), loc=2, borderaxespad=0.)
#        
#        
#        ax2 = ax1.twinx()          
#        ax2 .plot(step_sim, DNI_sim,'.-',color = '#39B8E3',label="DNI")
#        ax2.set_ylabel('DNI')
#        plt.legend(bbox_to_anchor=(1.15, .5), loc=2, borderaxespad=0.)
    
    return[output,hour_year_ini,hour_year_fin]        
     
