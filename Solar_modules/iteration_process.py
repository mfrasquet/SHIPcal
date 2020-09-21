# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 13:42:04 2016
Archivo que contiene las funciones de ITERACION

@author: Miguel Frasquet
"""
from Collector_modules.receivers import Rec_loss
from General_modules.func_General import thermalOil,moltenSalt
from iapws import IAPWS97
import numpy as np

def IT_flow (T_out_K,T_in_K,P_op_Mpa,temp_amb_K,REC_type,theta_i_rad,DNI,Long,IAM,Area,n_coll_loop):
    T_av_K=(T_in_K+T_out_K)/2
    average=IAPWS97(P=P_op_Mpa, T=T_av_K)
    Cp_av_KJkgK=average.cp
    
    Q_net_X=0
    for jj in range(1,202):
        if jj>=200: #Si no llegamos a convergencia después de 200 iteraciones paramos
            break
        if jj==1:
            err=99
        else:
            err=(Q_net-Q_net_X)/Q_net_X
            Q_net_X=Q_net
        
        if abs(err)<=1e-4: #Si el error de convergencia es suficientemente bajo salimos del bucle
            break
        DELTA_T_loss=T_out_K-temp_amb_K
        [Q_loss_rec]=Rec_loss(REC_type,DELTA_T_loss,theta_i_rad,DNI) #W/m
    
        Q_net=DNI*IAM*Area-Q_loss_rec*n_coll_loop*Long #In W
    
        flow_rate_kgs=(DNI*IAM*Area)/((T_out_K-T_in_K)*Cp_av_KJkgK*1000)
        T_out_K=T_in_K+Q_net/(flow_rate_kgs*Cp_av_KJkgK*1000)
        
    return [flow_rate_kgs,T_out_K,Q_loss_rec]
    
def IT_temp(fluidInput,T_in_K,P_op_Mpa,temp_amb_K,theta_i_rad,DNI,IAM,Area,n_coll_loop,flow_rate,REC_type,Long,rho_optic_0,**kwargs):    
    T_outlet_KX=999
    for jj in range(1,202):
        if jj>=200: #Si no llegamos a convergencia después de 200 iteraciones paramos
            break
        if jj==1:
            err=99
        else:
            err=(T_outlet_KX-T_outlet_K)/T_outlet_K
            T_outlet_KX=T_outlet_K
        
        if abs(err)<=1e-4: #Si el error de convergencia es suficientemente bajo salimos del bucle
            break
        
        T_av_K=(T_outlet_KX+T_in_K)/2
        
        if fluidInput=="water" or fluidInput=="steam":
            average=IAPWS97(P=P_op_Mpa, T=T_av_K)
            Cp_av_KJkgK=average.cp
        if fluidInput=="oil":
            [rho_av,Cp_av_KJkgK,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
        if fluidInput=="moltenSalt":
            [rho,Cp_av_KJkgK,k,Dv]=moltenSalt(T_av_K)
            
        
        DELTA_T_loss=T_outlet_KX-temp_amb_K
        [Q_loss_rec]=Rec_loss(REC_type,DELTA_T_loss,theta_i_rad,DNI)
        if Q_loss_rec<=0:
            Q_loss_rec=0
        
        gain=(DNI*Area*IAM*rho_optic_0-Q_loss_rec*n_coll_loop*Long)/(flow_rate*Cp_av_KJkgK*1000) #In W
        if jj<2 and gain<0: #To avoid iteration errors at the very beigning
            gain=0
        T_outlet_K=T_in_K+gain
    Perd_termicas=Q_loss_rec*n_coll_loop*Long 
    return[T_outlet_K,Perd_termicas]


def flow_calc (T_out_K,T_in_K,P_op_Mpa,temp_amb_K,theta_i_rad,DNI,IAM,Area,n_coll_loop,REC_type,Long,rho_optic_0,**kwargs):
    T_av_K=(T_in_K+T_out_K)/2
    average=IAPWS97(P=P_op_Mpa, T=T_av_K)
    Cp_av_KJkgK=average.cp
    
    DELTA_T_loss=T_out_K-temp_amb_K
    [Q_loss_rec]=Rec_loss(REC_type,DELTA_T_loss,theta_i_rad,DNI) #W/m
    flow_rate_kgs=(DNI*IAM*Area*rho_optic_0-Q_loss_rec*n_coll_loop*Long)/((T_out_K-T_in_K)*Cp_av_KJkgK*1000)

    Perd_termicas=Q_loss_rec*n_coll_loop*Long     
    return [flow_rate_kgs,Perd_termicas]

def flow_calcHTF (T_out_K,T_in_K,Cp_av,temp_amb_K,theta_i_rad,DNI,IAM,Area,n_coll_loop,REC_type,Long,rho_optic_0,**coll_par):
    
    DELTA_T_loss=T_out_K-temp_amb_K
    [Q_loss_rec]=Rec_loss(REC_type,DELTA_T_loss,theta_i_rad,DNI) #W/m
    flow_rate_kgs=(DNI*IAM*Area*rho_optic_0-Q_loss_rec*n_coll_loop*Long)/((T_out_K-T_in_K)*Cp_av*1000)

    Perd_termicas=Q_loss_rec*n_coll_loop*Long
    if flow_rate_kgs<=0:
        flow_rate_kgs=0
        Perd_termicas=0
        
    return [flow_rate_kgs,Perd_termicas]
def calcFRULFta(Cp_av_JkgK,Tm_Ta,mdot_permeter,rho_optic_0,eta1,eta2):
    #Calculates the U_L F' for that specific temperature differences.
    U_LF_av = eta1+eta2*(Tm_Ta) #The instantaneous U_L F' factor fot those mean temperature and ambient temperature.
    
    #Converts the U_LF' and F'(\tau \alpha)=rho_optic_0 into the U_LF_R and F_R(\tau \alpha) factors
    factor = 1 + (U_LF_av/(2*mdot_permeter*Cp_av_JkgK))
    
    F_Rta = rho_optic_0/factor
    
    F_RU_L = U_LF_av/factor
    
    return F_Rta,F_RU_L

def calc_nu_Tav_o2(T_av_K,temp_amb_K,DNI,IAM,rho_optic_0,eta1,eta2):
    Tm_Ta=T_av_K-temp_amb_K #Mean value to use the second order equation
    nu = IAM*rho_optic_0-eta1*(Tm_Ta)/DNI-eta2*((Tm_Ta)**2)/DNI#Calculates the efficiency in that hour under that specific DNI and Tm-Ta
    
    return nu

def calc_nu_Ti_o1(F_Rta,F_RU_L,DNI,IAM,T_in_K,temp_amb_K):
    nu = F_Rta*IAM -F_RU_L*(T_in_K-temp_amb_K)/DNI
    
    return nu

def calc_T_out_wo2(Area_coll,rho_optic_0,eta1,eta2,mdot_test_permeter,Cp_av_JkgK,T_in_K,temp_amb_K,DNI,IAM,Tm_Ta):
    #This equation was gotten through a lot of algebra and using equations 6.17.3, 6.17.4, 6.17.5, 6.17.6, 6.19.2a, 6.19.3a from Duffie, J. 2013
    #Broadly this is a form to calculate the outlet temperature of a collector with a quadratic efficiency curve for mean collector temperature - weather temperature but only with the inlet temperature
    
    w = eta1 + 0.5*eta2*T_in_K - eta2*temp_amb_K
    
    a = -0.5*eta2
    b = 2*mdot_test_permeter*Cp_av_JkgK - w + 0.5* eta2*T_in_K + eta2*(T_in_K-temp_amb_K)
    c = w*(T_in_K + 2*(T_in_K-temp_amb_K)) - 2*mdot_test_permeter*Cp_av_JkgK*T_in_K - 2*DNI*IAM*rho_optic_0
    
    #Using roots was taking a looot of time
    
    #coeff = [a,b,c]
    
    #To1,To2 = np.roots(coeff) #Since it is a quadratic equation I have two results and I have to choose the right one
    
    discriminant = b**2 - 4*a*c
    
    if discriminant >= 0:
        To1 = (-b + np.sqrt(discriminant))/(2*a)
        To2 = (-b - np.sqrt(discriminant))/(2*a)
        if To1 > 0 and To1 > T_in_K and abs(To1 - T_in_K) < 300: #First it has to be real #If the To1 result is real it has to be possitive, greater than the inlet temperature and it shall not be way bigger than the inlet temperature. I arbitrary chose a 100 treshold
            T_out_K_colln = To1
        elif To2 > T_in_K and abs(To2 - T_in_K) < 300: #If from the beggining the To1 was complex, then I check the To2 result to be real and be larger than T_in_K
            T_out_K_colln = To2
        else: #If everything fails, say both results are negative I use an broad aproximation as follows:
            F_Rta,F_RU_L = calcFRULFta(Cp_av_JkgK,Tm_Ta,mdot_test_permeter,rho_optic_0,eta1,eta2) #Calculates the F_Rta and F_RU_L for the tm using the inlet temperature of design for the proces and teh outlet of design
            aprox_efficiency_nu_coll2 = calc_nu_Ti_o1(F_Rta,F_RU_L,DNI,IAM,T_in_K,temp_amb_K) #Calculates the efiiciency using the linear equation
            T_out_K_colln = T_in_K+((DNI*aprox_efficiency_nu_coll2)/(mdot_test_permeter*Cp_av_JkgK)) #Then the output emperature
    else: #If everything fails, say both results are negative I use an broad aproximation as follows:
        F_Rta,F_RU_L = calcFRULFta(Cp_av_JkgK,Tm_Ta,mdot_test_permeter,rho_optic_0,eta1,eta2) #Calculates the F_Rta and F_RU_L for the tm using the inlet temperature of design for the proces and teh outlet of design
        aprox_efficiency_nu_coll2 = calc_nu_Ti_o1(F_Rta,F_RU_L,DNI,IAM,T_in_K,temp_amb_K) #Calculates the efiiciency using the linear equation
        T_out_K_colln = T_in_K+((DNI*aprox_efficiency_nu_coll2)/(mdot_test_permeter*Cp_av_JkgK)) #Then the output emperature
        
    return T_out_K_colln

def equiv_coll_series_o1(T_out_K,temp_amb_K,DNI,IAM,Area,Cp_av_JkgK,T_in_K,Area_coll,rho_optic_0,eta1,eta2,mdot_test_permeter,**kwargs):#This function calculates the equivalent o1 parameters of an array of collectors connected in series using their o2 parameters.

    Tm_Ta=0.5*(T_in_K + T_out_K)-temp_amb_K #Difference of of the mean value of the design temperatures to use the second order equation for broad aproximations as last resort.
    
    #In order to consider the collectors in the serie
    #Variable intialization
    T_out_K_coll1 = calc_T_out_wo2(Area_coll,rho_optic_0,eta1,eta2,mdot_test_permeter,Cp_av_JkgK,T_in_K,temp_amb_K,DNI,IAM,Tm_Ta) #Calculates the outlet temperature of the first collector. This will be used for the inlet temperature of the second collector
    if T_out_K_coll1 < T_in_K:
        return 1,float('inf'),mdot_test_permeter
    Tm_Ta_coll1 = 0.5*(T_out_K_coll1+T_in_K)-temp_amb_K #The diference of the mean temperature and the weather temperature,needed to calculate the initial F_Rta and F_RU_L corresponding to the first collector
    F_Rta_coll1,F_RU_L_coll1 = calcFRULFta(Cp_av_JkgK,Tm_Ta_coll1,mdot_test_permeter,rho_optic_0,eta1,eta2) #Calculates F_Rta and F_RU_L corresponding to the first collector
    
    if kwargs['auto']=='on': #Faster aproximation as in Duffie, it doesn't take into account the changes in in F_RU_L_av from the Tm
        n = int(Area/Area_coll)
        k=F_RU_L_coll1/(mdot_test_permeter*Cp_av_JkgK)
        beta = (1-(1-k)**n)/(n*k)
        F_Rta_coll1*=beta
        F_RU_L_coll1*=beta
    else:
    
        Area_coll_series = Area_coll #At the beginning there is only one coll in the serie
        
        while abs(Area_coll_series - Area) > 0.0001 or Area_coll_series > Area+0.5*Area_coll: #The loop will stop when the same area "Area" which was n_coll_loop*Area_coll is reached, it is to say when I considered already all the collectors in the loop.
            T_out_K_colln = calc_T_out_wo2(Area_coll,rho_optic_0,eta1,eta2,mdot_test_permeter,Cp_av_JkgK,T_out_K_coll1,temp_amb_K,DNI,IAM,Tm_Ta) #The next collector doesn't care where does the inlet water comes from so I can use the same efficiency curve to calculate the outlet temperature in this collector
            Tm_Ta_colln = 0.5*(T_out_K_colln+T_out_K_coll1)-temp_amb_K #The diference of the mean temperature and the weather temperature,needed to calculate the F_Rta and F_RU_L corresponding to the n collector
            F_Rta_colln,F_RU_L_colln = calcFRULFta(Cp_av_JkgK,Tm_Ta_colln,mdot_test_permeter,rho_optic_0,eta1,eta2) #Calculates F_Rta and F_RU_L corresponding to the n collector
            
            #Now that the parameters of the efficiency curve of the n-1 previous collectors and the n collector are known the equivalent parameters are calcualted
            
            k = F_RU_L_colln/(mdot_test_permeter*Cp_av_JkgK) #k factor needed for the equivalent equation as in Duffie, J 2013. The second collector is always the same
            
            F_Rta_eq = (Area_coll_series*F_Rta_coll1*(1-k) + Area_coll*F_Rta_colln)/(Area_coll_series+Area_coll) #Equivalences obtained for the previous equivalent collector an +1 collector in series each time as in Duffie, J 2013
            
            F_RU_L_eq = (Area_coll_series*F_RU_L_coll1*(1-k) + Area_coll*F_RU_L_colln)/(Area_coll_series+Area_coll)
            
            F_Rta_coll1,F_RU_L_coll1 = F_Rta_eq,F_RU_L_eq #Now I consider the equivalent parameters as if they were from a first collector for the adding of the n+1 collector
            T_out_K_coll1 = T_out_K_colln #Now the output of the n collector is the output of the equivalent collector which will be used for the inlet in the next collector
            Area_coll_series += Area_coll #Now the equivalent collector has a total area of the previous area plus the area of one collector
    return F_Rta_coll1,F_RU_L_coll1,mdot_test_permeter
    #return F_Rta_eq,F_RU_L_eq,Area_coll_series,mdot_test_kgs


def analytic_otemp(fluidInput,T_out_K,P_op_Mpa,temp_amb_K,DNI,IAM,Area,n_coll_loop,mdot_use_kgs,T_in_K,F_Rta_eq,F_RU_L_eq,mdot_test_permeter,**kwargs):
    #This calculates the outlet temperature for the collectors in the loop with a given flux
    T_av_K=0.5*(T_in_K+T_out_K) #[K]
    if fluidInput == 'water':
        #the average of temperatures is take and then twith help of IAPWS97 the Cp is obtained.
        Cp_av_JkgK=IAPWS97(P=P_op_Mpa, T=T_av_K).cp*1000 #[J/kg·K]
    elif fluidInput=="oil":
        [rho_av,Cp_av_KJkgK,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
        Cp_av_JkgK = Cp_av_KJkgK*1000
    elif fluidInput=="moltenSalt":
        [rho,Cp_av_KJkgK,k,Dv]=moltenSalt(T_av_K)
        Cp_av_JkgK = Cp_av_KJkgK*1000
    
    #Get the linear parameters for the whole loop of collectors depenent of radiation, Ti and Ta
    #F_Rta_eq,F_RU_L_eq,mdot_test_kgs = equiv_coll_series_o1(T_in_K,T_out_K,temp_amb_K,DNI,IAM,Area,Cp_av_JkgK,**coll_par) #Calculates the equivalent o1 parameters of an array of collectors connected in series using their o2 parameters.
    
    #Calculate nu for the linear efficiency equation
    nu_test = calc_nu_Ti_o1(F_Rta_eq,F_RU_L_eq,DNI,IAM,T_in_K,temp_amb_K)
    
    #Modify nu for the flux of use
    r= (mdot_use_kgs*Cp_av_JkgK*(1-(1-(F_RU_L_eq/(mdot_test_permeter*Cp_av_JkgK)))**((Area*mdot_test_permeter)/mdot_use_kgs)))/(F_RU_L_eq*Area)
    nu_use = r*nu_test #Efficiency at use conditions
    
    #Calculates the outlet temperature
    T_outlet_K = T_in_K + DNI*Area*nu_use/(mdot_use_kgs*Cp_av_JkgK)
    Perd_termicas=(1 - nu_use)*DNI*Area#[W]
    Q_prod=(nu_use)*DNI*Area*.001#[kW]
    
    return [T_outlet_K,Q_prod,Perd_termicas]

def flow_calc_gen(fluidInput,T_out_K,P_op_Mpa,temp_amb_K,DNI,IAM,Area,T_in_K,F_Rta_eq,F_RU_L_eq,mdot_test_permeter, **kwargs):
    #This function uses the general efficiency equation.
    #This is used only for water and steam.
    #In order to calculate a specific heat at constant preassure (Cp) for water secific for the temperature changes
    #the average of temperatures is take and then twith help of IAPWS97 the Cp is obtained.
    T_av_K=0.5*(T_in_K+T_out_K) #[K]
    
    if fluidInput == 'water':
        #the average of temperatures is take and then twith help of IAPWS97 the Cp is obtained.
        Cp_av_JkgK=IAPWS97(P=P_op_Mpa, T=T_av_K).cp*1000 #[J/kg·K]
    elif fluidInput=="oil":
        [rho_av,Cp_av_KJkgK,k_av,Dv_av,Kv_av,thermalDiff_av,Prant_av]=thermalOil(T_av_K)
        Cp_av_JkgK = Cp_av_KJkgK*1000 #[J/kg·K]
    elif fluidInput=="moltenSalt":
        [rho,Cp_av_KJkgK,k,Dv]=moltenSalt(T_av_K)
        Cp_av_JkgK = Cp_av_KJkgK*1000 #[J/kg·K]
    
    #So far a efficiency curve for the whole loop has been obtained at the test flow rate and now this curve equivalent to a huge collector with the sum of the areas has to be modified regarding the flux to obtain the desired temperature
    
    epsilon = T_out_K-T_in_K #This is the target jump in temperature.
    nu_test = calc_nu_Ti_o1(F_Rta_eq,F_RU_L_eq,DNI,IAM,T_in_K,temp_amb_K) #This is the efficiency at the test flux for the design temperature jump.
    
    if ((F_RU_L_eq*epsilon)/(DNI*nu_test))>=1 or ((F_RU_L_eq)/(mdot_test_permeter*Cp_av_JkgK))>=1: #This is because in this case the ln_den is not defined because the argument of the logarithm is too near 0 or negative, in this case the result either is imaginary or inf and therefore is handeled harcoded resulting in a flux = 0 and all the radiation being lost.
        mdot_use_kgs = 0
        Perd_termicas = DNI*Area #Originally the DNI is in [W/m2]
    else:
        #Obtained from eq 6.20.3, 6.20.4 and 10.5.2. Calculate the flux needed to obtain the desired jum taking into account the cahnges in the efficiency due the changes in the flux relative to the test flux.
        ln_num = np.log(1-((F_RU_L_eq)/(mdot_test_permeter*Cp_av_JkgK)))
        ln_den = np.log(1-((F_RU_L_eq*epsilon)/(DNI*nu_test)))
    
        mdot_use_kgs = mdot_test_permeter*Area*(ln_num/ln_den)
        
        #The proportionality factor "r" between the eficiency at test conditions and at use conditions by rearranging 6.20.3 and 6.20.4 from Duffie, J. 2013
        r= (mdot_use_kgs*Cp_av_JkgK*(1-(1-(F_RU_L_eq/(mdot_test_permeter*Cp_av_JkgK)))**(mdot_test_permeter*Area/mdot_use_kgs)))/(F_RU_L_eq*Area)
        nu_use = r*nu_test #Efficiency at use conditions
        
        #It is needed to calculate the final jump in the temperature for this case to see if we are near enough to the target temperature
        #T_out_K_colln = T_in_K + DNI*Area*nu_use/(mdot_use_kgs*Cp_av_JkgK)
        #print(T_out_K_colln)
        
        Perd_termicas=(1 - nu_use)*DNI*Area
        
    Q_prod=DNI*Area*0.001 - Perd_termicas*0.001#[kW]
        
    return [mdot_use_kgs,Q_prod,Perd_termicas]