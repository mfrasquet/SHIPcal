#Function to get meteo data from M61 data file
#MFH 26/7/16
def Meteo_data (file_meteo):
    import numpy as np
    data = np.loadtxt(file_meteo, delimiter="\t")
    DNI=data[:,8]
    temp=data[:,9]
    return [data,DNI,temp]
