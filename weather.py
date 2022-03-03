from pathlib import Path

import numpy as np

class Weather:
    """
    This class handles the TMY file reads and prepare the variables to
    return the weather state at any hour of the simulation.
    
    Assumes solar time.
    """
    
    def __init__(self, location_file, mofDNI=1):
        self.mofDNI = mofDNI
        self.location_file = location_file
        [
            self._lat, self._lon, self._elev, 
            self._tz_loc, self._DNI, self._GHI, 
            self._T_amb
        ] = self.read_file()
        self.set_T_grid()
    
    def read_file(self):
        """ 
        Gets file location, reads its content and stores its data in
        this class variables.
        
        Modify this method if your TMY does not have the standard format.
        """
        
        with open(self.location_file, "r") as tmy:
            tmy.readline()
            location_data = tmy.readline()
        lat, lon, elev, tz_loc = location_data.split()
        
        tmy = np.loadtxt(self.location_file, skiprows=4)
        
        DNI = tmy[:,5]*self.mofDNI
        GHI = tmy[:,6]*self.mofDNI
        T_amb = tmy[:,7]
        return lat, lon, elev, tz_loc, DNI, GHI, T_amb
     
    def interpolate_prop(self, h_id, prop_array):
        """ Interpolate the property to a fractional index of the array """
        h_floor = int(np.floor(h_id))
        h_ceil = int(np.ceil(h_id))
        dh = h_ceil-h_floor
        if dh == 0:
            return prop_array[h_floor]
        dprop = prop_array[h_ceil]-prop_array[h_floor]
        
        prop = prop_array[h_floor] + (dprop/dh)*(h_id-h_floor)
        
        return prop
        
    @property
    def tz_loc(self):
        """ [-] Int. Timezone of the location in simulation """
        return self._tz_loc

    @property
    def elev(self):
        """ [m] Float. Height above sea level """
        return self._elev
        
    @property
    def lat(self):
        """ [°] Float. Latitude of location in simulation """
        return self._lat
    
    @property
    def lon(self):
        """ [°] Float. Longitude of location in simulation. """
        return self._lon
        
    @property
    def location_file(self):
        """ String. Location of the TMY file currently used """
        return self._location_file
    
    @location_file.setter
    def location_file(self, path_to_file):
        self._location_file = Path(path_to_file)
        if not self.location_file.exists():
            raise ValueError(f"No such file {path_to_file}.")
        self.read_file()

    def get_DNI(self, h=None):
        if h:
            return self.interpolate_prop(h, self._DNI)
                
        else:
            return self._DNI
    
        
    DNI = property(
        get_DNI,
        doc=""" [W/m^2] Hourly array. Direct Normal Irradiation (DNI). """
    )

    def get_GHI(self, h=None):
        """ [W/m^2] Hourly array. Global Horizontal Irradiation (GHI). """
        if h:
            return self.interpolate_prop(h, self._GHI)
                
        else:
            return self._GHI
    
        
    GHI = property(
        get_GHI,
        doc=""" [W/m^2] Hourly array. Global Horizontal Irradiation (GHI). """
    )
    
    def get_T_amb(self, h=None):
        if h:
            return self.interpolate_prop(h, self._T_amb)
                
        else:
            return self._T_amb


    T_amb = property(
        get_T_amb,
        doc=""" [°C] Hourly array. Ambient temperature. """
    )

    def get_T_grid(self, h=None):
        if h:
            return self.interpolate_prop(h, self._T_grid)
                
        else:
            return self._T_grid

    def set_T_grid(self):
        """ 
        This method computes the water temperature in grid from 
        the ambient temperature property. 
        """
        T_amb_mean = self.T_amb.mean()
        T_amb_max = self.T_amb.max()
        
        # The offset, lag, and ratio values were obtained by fitting data
        # compiled by Abrams and Shedd [8], the FloridaSolar Energy 
        # Center [9], and Sandia National Labs
        offset = 3
        ratio = 0.22 + 0.0056*(T_amb_mean - 6.67)
        lag = 1.67 - 0.56*(T_amb_mean - 6.67)
        
        T_in_C_AR=[]
        
        for day in range(365):
            #The hourly year array is built by the temperature calculated for the day printed 24 times for each day
            #This was taken from TRNSYS documentation.
            T_in_C_AR+=[(T_amb_mean+offset)+ratio*(T_amb_max/2)*np.sin(np.radians(-90+(day-15-lag)*360/365))]*24
        
        self._T_grid = np.array(T_in_C_AR)
    
    T_grid = property(
        get_T_grid,
        set_T_grid,
        doc=""" [°C] Hourly array. Water temperature from grid. """
    )
    
    def get_humidity(self, h=None):
        if h:
            return self.interpolate_prop(h, self._humidity)
                
        else:
            return self._humidity

    humidity = property(
        get_humidity,
        doc=""" [-] Hourly array. Relative humidity. """
    )

    def get_wind_speed(self, h=None):
        if h:
            return self.interpolate_prop(h, self._wind_speed)
                
        else:
            return self._wind_speed
    
    def set_wind_speed(self, hourly_wind_speed):
        self._wind_speed = hourly_wind_speed
        
    wind_speed = property(
        get_wind_speed,
        set_wind_speed,
        doc=""" [m/s] Hourly array. Wind speed. """
    )
    
if __name__ == "__main__":
    location_file = Path(
        "/home/jaarpa/aProjects/solatom/SHIPcal/tests/Celaya.dat"
    )
    celaya = Weather(location_file)
    
    print(celaya.T_amb.mean())
    print(celaya.T_amb[2])
    print(celaya.get_T_amb(2.1))
    print(celaya.get_T_amb(2.5))
    print(celaya.get_T_amb(2.9))
    print(celaya.get_T_amb(3))