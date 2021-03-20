#Function to evaluate the characteristic day of each month from a Meteo file
#MFH 26/7/16

def char_day(file_loc):
 
    import numpy as np
    from Meteo_data import Meteo_data
       
    [data,DNI,temp]=Meteo_data (file_loc)
    
    #Design Point
    DNI_matrix = np.zeros(shape=(12,24))
    T_amb_matrix= np.zeros(shape=(12,24))
    days_matrix= np.zeros(shape=(12,24))
    days_t_matrix= np.zeros(shape=(12,24))  
    
    for m1 in range(0,12):
        for h1 in range(0,24):
            for i in range(0,8760):
                #check1=data[i,0]
                #check2=data[i,2]
                if data[i,0]==m1+1 and data[i,2]==h1+1:
                   # aa=data[i,8]
                   # bb=data[i,9]
                    DNI_matrix[m1,h1]=data[i,8]+DNI_matrix[m1,h1]
                    T_amb_matrix[m1,h1]=data[i,9]+T_amb_matrix[m1,h1]
                    days_t_matrix[m1,h1]=1+days_t_matrix[m1,h1]
                    if data[i,8]>0:
                        days_matrix[m1,h1]=1+days_matrix[m1,h1]
                        
    for m1 in range(0,12):
        for h1 in range(0,24):
            if days_matrix[m1,h1]==0:
                days_matrix[m1,h1]=1
                
    DNI2=DNI_matrix/days_matrix
    T_amb2=T_amb_matrix/days_t_matrix
    return [DNI2,T_amb2]                   
    
