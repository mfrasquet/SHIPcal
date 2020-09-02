
#Miguel Frasquet

import numpy as np
import math
#from matplotlib import pyplot as plt

def bar_MPa(pres):
    pres=pres/10
    return pres
def MPa_bar(pres):
    pres=pres*10
    return pres
def C_K(temp):
    temp=temp+273
    return temp
def K_C(temp):
    temp=temp-273
    return temp
    
def check_overwrite(data,reg,rebaja,num_loops,n_coll_loop,type_integration,almVolumen,correccionDNI,FS):
    flag_n_coll_loop=False;flag_rebaja=False;flag_num_loops=False;flag_type_integration=False;flag_almVolumen=False;flag_correccionDNI=False;flag_FS=False
    if data.at[reg,'rebaja']==rebaja:
        pass
    else:
        flag_rebaja=True
    if data.at[reg,'num_loops'] == num_loops: 
        pass
    else:
        flag_num_loops=True
    if data.at[reg,'n_coll_loop'] == n_coll_loop:
        pass
    else:
        flag_n_coll_loop=True
    if data.at[reg,'type_integration'] == type_integration:
        pass
    else:
        flag_type_integration=True
    if data.at[reg,'almVolumen'] == almVolumen:
        pass
    else:
        flag_almVolumen=True
    if data.at[reg,'correccionDNI'] == correccionDNI:
        pass
    else:
        flag_correccionDNI=True
    if data.at[reg,'FS'] == FS:
        pass
    else:
        flag_FS=True
    
    flagOverwrite=[flag_rebaja,flag_num_loops,flag_n_coll_loop,flag_type_integration,flag_almVolumen,flag_correccionDNI,flag_FS]        
    return flagOverwrite
    

def calc_hour_year(mes,dia,hora): #This function calculates what is the correspondign hour of the year for an specific date and time.
    mes_days=(31,28,31,30,31,30,31,31,30,31,30,31)
    
    num_days=0 #Initializate the variables
    cont_mes=mes-1
    if mes<=12: #Check that the month input is reliable
        while (cont_mes >0):
            cont_mes=cont_mes-1 #Counts backwards from the introduced month to the first month in the year(January)
            num_days=num_days+mes_days[cont_mes] #Adds all the days in the months previous to the introduced one
        if dia<=mes_days[mes-1]: #Checks that the introduced dau number is smaller than the number of days in that month
            num_days=num_days+dia #Adds the quantity of days passed so far in the introduced month
        else:
            raise ValueError('Day should be <=days_month')    
    else:
        raise ValueError('Month should be <=12')
    
    if hora<=24: #Checks that the hour number is less than 24
        hour_year=(num_days-1)*24+hora #Minus the 24 h of the current day, and adds the hours that have passed in the current day #Calculates the current year hour
    else:
       raise ValueError('Hour should be <=24')
       #The minimum output hour year is 1
    return hour_year

   
    
def DemandData(file_demand,mes_ini_sim,dia_ini_sim,hora_ini_sim,mes_fin_sim,dia_fin_sim,hora_fin_sim): #Returns the only the entries of the demand vector (consumtpion for every hour along the year) that corresponds to the hours between the the starting and ending hours of the simulation
    
#    Demand = np.loadtxt(file_demand, delimiter=",")
    Demand=np.array(file_demand)
    
    hour_year_ini=calc_hour_year(mes_ini_sim,dia_ini_sim,hora_ini_sim)
    hour_year_fin=calc_hour_year(mes_fin_sim,dia_fin_sim,hora_fin_sim)
    
    if hour_year_ini <= hour_year_fin:
        sim_steps=hour_year_fin-hour_year_ini
    else:
        raise ValueError('End time is smaller than start time') 


    #Bucle de simulacion
    Demand_sim=np.zeros (sim_steps)
    step_sim=np.zeros (sim_steps)
    
    
    step=0
    for step in range(0,sim_steps):
        step_sim[step]=step
        Demand_sim[step]=Demand[hour_year_ini+step-1]
      
        step+=1
        
#    if plot_Demand==1:
#        fig = plt.figure()
#        fig.suptitle('Demand', fontsize=14, fontweight='bold')
#        ax2 = fig.add_subplot(111)         
#        ax2 .plot(step_sim, Demand_sim,'.-',color = 'b',label="Demand_sim")
#    
#        ax2.set_xlabel('simulation')
#        ax2.set_ylabel('kWh')
#        plt.legend(bbox_to_anchor=(1.05, 1), loc=1, borderaxespad=0.)
    
    return Demand_sim

def annualConsumpFromSHIPcal(activeHoursArray,activeDaysWeekArray,activeMonthsArray,annualConsumptionkWh):
    #Una vez tengo los arrays lo convierto en horario
    findes_array=[3,0,3,2,3,2,3,3,2,3,2,3] #Vector findes es 28-el numero de días de cada mes, suponemos 28=4 semanas
    
    #Vectores día de la semana combinados con el vector diario
    lunes_array=list(np.array(activeHoursArray)*activeDaysWeekArray[0])
    martes_array=list(np.array(activeHoursArray)*activeDaysWeekArray[1])
    miercoles_array=list(np.array(activeHoursArray)*activeDaysWeekArray[2])
    jueves_array=list(np.array(activeHoursArray)*activeDaysWeekArray[3])
    viernes_array=list(np.array(activeHoursArray)*activeDaysWeekArray[4])
    sabado_array=list(np.array(activeHoursArray)*activeDaysWeekArray[5])
    domingo_array=list(np.array(activeHoursArray)*activeDaysWeekArray[6])
    
    #Vector semana
    semana_array=lunes_array+martes_array+miercoles_array+jueves_array+viernes_array+sabado_array+domingo_array
    
    #Vector mes
    Enero_array=list(np.array(4*semana_array+lunes_array*findes_array[0])*activeMonthsArray[0])
    Febrero_array=list(np.array(4*semana_array+lunes_array*findes_array[1])*activeMonthsArray[1])
    Marzo_array=list(np.array(4*semana_array+lunes_array*findes_array[2])*activeMonthsArray[2])
    Abril_array=list(np.array(4*semana_array+lunes_array*findes_array[3])*activeMonthsArray[3])
    Mayo_array=list(np.array(4*semana_array+lunes_array*findes_array[4])*activeMonthsArray[4])
    Junio_array=list(np.array(4*semana_array+lunes_array*findes_array[5])*activeMonthsArray[5])
    Julio_array=list(np.array(4*semana_array+lunes_array*findes_array[6])*activeMonthsArray[6])
    Agosto_array=list(np.array(4*semana_array+lunes_array*findes_array[7])*activeMonthsArray[7])
    Septiembre_array=list(np.array(4*semana_array+lunes_array*findes_array[8])*activeMonthsArray[8])
    Octubre_array=list(np.array(4*semana_array+lunes_array*findes_array[9])*activeMonthsArray[9])
    Noviembre_array=list(np.array(4*semana_array+lunes_array*findes_array[10])*activeMonthsArray[10])
    Diciembre_array=list(np.array(4*semana_array+lunes_array*findes_array[11])*activeMonthsArray[11])
    
    #vector anual
    anual_array=Enero_array+Febrero_array+Marzo_array+Abril_array+Mayo_array+Junio_array+Julio_array+Agosto_array+Septiembre_array+Octubre_array+Noviembre_array+Diciembre_array
    
    #Consumo anual horario (potencia asumida constante durante toda la hora)
    if np.sum(anual_array)==0:
        consumo_anual_horario=0
    else:
        consumo_medio_diario=annualConsumptionkWh/np.sum(anual_array) #kW cada hora
        consumo_anual_horario=np.array(anual_array)*consumo_medio_diario #Consumo que debe de ser metido en la base de datos
    return consumo_anual_horario
    
def waterFromGrid(T_in_C_AR_mes):
    
    T_in_C_AR=np.zeros(8760)
    for ii in range(0,8760):
        if (ii<=744-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[0]
        if (ii>744-1) and (ii<=1416-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[1]
        if (ii>1416-1) and (ii<=2160-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[2]        
        if (ii>2160-1) and (ii<=2880-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[3]        
        if (ii>2880-1) and (ii<=3624-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[4]        
        if (ii>3624-1) and (ii<=4344-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[5]        
        if (ii>4344-1) and (ii<=5088-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[6]        
        if (ii>5088-1) and (ii<=5832-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[7]        
        if (ii>5832-1) and (ii<=6552-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[8]
        if (ii>6552-1) and (ii<=7296-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[9]
        if (ii>7296-1) and (ii<=8016-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[10]
        if (ii>8016-1):
            T_in_C_AR[ii]=T_in_C_AR_mes[11]      
            
    return (T_in_C_AR)


def waterFromGrid_trim(T_in_C_AR,mes_ini_sim,dia_ini_sim,hora_ini_sim,mes_fin_sim,dia_fin_sim,hora_fin_sim):
    
    hour_year_ini=calc_hour_year(mes_ini_sim,dia_ini_sim,hora_ini_sim)#Calls a function within this same script yo calculate the corresponding hout in the year for the day/month/hour of start and end
    hour_year_fin=calc_hour_year(mes_fin_sim,dia_fin_sim,hora_fin_sim)
    
    if hour_year_ini <= hour_year_fin: #Checks that the starting hour is before than the enfing hour
        sim_steps=hour_year_fin-hour_year_ini #Stablishes the number of steps as the hours between the starting and ending hours
    else:
        raise ValueError('End time is smaller than start time')   
    
    T_in_C_AR_trim=np.zeros (sim_steps)
    
    step=0
    for step in range(0,sim_steps):
        T_in_C_AR_trim[step]=T_in_C_AR[hour_year_ini+step-1]
        step+=1
    
    return (T_in_C_AR_trim)        
        

def waterFromGrid_v2(T_in_C_AR_mes):
    days_in_the_month=[31,28,31,30,31,30,31,31,30,31,30,31] #days_in_the_month[month_number]=how many days are in the month number "month_number"
    T_in_C_AR=[] #Creates an empty list where I'll store the temperatures per hour along the year.
    for month in range(12): #For eacho month
        T_in_C_AR+=[T_in_C_AR_mes[month]]*(days_in_the_month[month]*24) #Append the average temperature from the grid number_of_days_in_the_month*24 times
    return(np.array(T_in_C_AR)) #Returns the list transformed to an array.

def waterFromGrid_v3(file_meteo, sender='CIMAV'):
    if sender=='CIMAV':
        Tamb = np.loadtxt(file_meteo, delimiter="\t", skiprows=4)[:,7]#Reads the temperature of the weather. The TMYs are a bit different.
    elif sender=='SHIPcal':
        from simforms.models import Locations, MeteoData
        meteo_data = MeteoData.objects.filter(location=Locations.objects.get(pk=file_meteo))
        Tamb = meteo_data.order_by('hour_year_sim').values_list('temp',flat=True)
    else:
        Tamb = np.loadtxt(file_meteo, delimiter="\t")[:,9]#Reads the temperature of the weather
    TambAverage=np.mean(Tamb) #Computes the year average
    TambMax=np.amax(Tamb) #Computes the maximum temperature
    
    offset = 3 #A defined offset of 3 °C
    ratio = 0.22 + 0.0056*(TambAverage - 6.67)
    lag = 1.67 - 0.56*(TambAverage - 6.67)
#The offset, lag, and ratio values were obtained by fitting data compiled by Abrams and Shedd [8], the FloridaSolar Energy Center [9], and Sandia National Labs
    
    T_in_C_AR=[] #It is easier to work with this array as a list first to print 24 times the mean value of the water temperature for every day
    
    for day in range(365):
        #The hourly year array is built by the temperature calculated for the day printed 24 times for each day
        T_in_C_AR+=[(TambAverage+offset)+ratio*(TambMax/2)*np.sin(np.radians(-90+(day-15-lag)*360/365))]*24 #This was taken from TRNSYS documentation.
    
    return np.array(T_in_C_AR)

def thermalOil(T): #Function to derive the properties of thermal oil from the Thermal oil DB
    T=T-273 #To transform K to C
    if T==0:
        T=0.001
    else:
        pass
    #Density kg/m3
    rho=-0.6388*T+885.61
    #Specific Heat kJ/kgK
    Cp=0.0038*T+1.8074
    #Thermal conductivity W/mK
    k=-9e-5*T+.1376
    #Dinamic viscosity #kg/m*s
    Dv=(23428.38511*T**(-1.89020))*1e-3
    #Kinematic viscosity m2/s
    Kv=(19563.70818*T**-1.80379)*1e-6
    #Thermal Diffusivity m2/s
    thermalDiff=8.20353*np.exp(-0.00135*T)*1e-8
    #PrantNumber
    Prant=177506.92794*T**(-1.68808)
    return(rho,Cp,k,Dv,Kv,thermalDiff,Prant)
    
    
def moltenSalt(T): #Function to derive the properties of molten Salts from Solar Salt SQM
 
    T=T-273 #To transform K to C
    if T==0:
        T=0.001
    else:
        pass
 
    #Density kg/m3
    rho=-0.636*T+2090
    #Specific Heat kJ/kgK
    Cp=max(1.6,0.000172*T+1.44)
    #Thermal conductivity W/mK
    k=1.89e-4*T+.441
    #Dinamic viscosity #kg/m*s
    try:
        Dv=0.0231*math.exp(-6.17e-3*T)
    except:
        Dv=0.001 #To avoid errors when iteration process explores high boundaries


    return(rho,Cp,k,Dv)
 

 

def reportOutputOffline(reportsVar):
    print("")
    print("////////////////// Results from SHIPcal v."+reportsVar['version']+" ///////////////////")
    print("Location: "+reportsVar['location']+" ("+str(round(reportsVar['DNI_anual_irradiation'],2))+" kWh with ModfDNI: "+str(reportsVar['mofDNI'])+")")
    print("Solar plant: "+str(int(reportsVar['Area_total']*1.5))+" m2 with "+str(reportsVar['n_coll_loop'])+" collectors per loop, in "+str(reportsVar['num_loops'])+" loops")
    print("Storage: "+str(int(reportsVar['energyStored']))+" kWh")
    print("Integration scheme: "+reportsVar['type_integration'])
    print("/// SOLAR PRODUCTION:")
    print("Energy demand of the industry "+str(round(reportsVar['Demand_anual'],2))+" kWh")
    print("Gross solar production: "+str(round(reportsVar['Production_max'],2))+" kWh with ModfProd: "+str(reportsVar['mofProd'])+"  ("+str(int(reportsVar['solar_fraction_max']))+" %)")
    print("Net solar production: "+str(round(reportsVar['Production_lim'],2))+" kWh with ModfProd: "+str(reportsVar['mofProd'])+" ("+str(int(reportsVar['solar_fraction_lim']))+" %)")
    print("Utilization ratio: "+str(round(reportsVar['Utilitation_ratio'],2))+" %")
    print("/// FINANCE:")
    print("Investment: "+str(int(reportsVar['Selling_price']))+" $")
    print("Savings 1st year: "+str(int(reportsVar['Energy_savingsList'][1]))+" $ with ModfInv: "+str(reportsVar['mofINV'])+"")
    print("Payback period: "+str(int(reportsVar['AmortYear']))+" years")