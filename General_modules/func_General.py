
#Miguel Frasquet

import numpy as np
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
    

def calc_hour_year(mes,dia,hora):
    mes_string=("Ene","Feb","Mar","Apr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dec")
    mes_days=(31,28,31,30,31,30,31,31,30,31,30,31)
    
    num_days=0
    cont_mes=mes-1
    if mes<=12:
        while (cont_mes >0):
            cont_mes=cont_mes-1
            num_days=num_days+mes_days[cont_mes]
        if dia<=mes_days[mes-1]:
            num_days=num_days+dia
        else:
            raise ValueError('Day should be <=days_month')    
    else:
        raise ValueError('Month should be <=12')
    
    if hora<=24:
        hour_year=(num_days-1)*24+hora
    else:
       raise ValueError('Hour should be <=24') 
    return hour_year

   
    
def DemandData(file_demand,mes_ini_sim,dia_ini_sim,hora_ini_sim,mes_fin_sim,dia_fin_sim,hora_fin_sim):
    
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

def annualConsumpFromRessspi(activeHoursArray,activeDaysWeekArray,activeMonthsArray,annualConsumptionkWh):
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