"""
This file contains the classes that define the collector in
shipcal
"""

from shipcal.elements import Element

import pandas as pd

class FresnelOptics():
    """
    Class for the optics in Linear Fresnel collectors.
    eff_opt_norm => Optical efficiency at normal incidence [-]
    iam_file => IAM file for the collector [csv]
    azimuth_field => azimuth of the solar field [deg]
    roll_field => roll of the solar field [deg]
    pitch_field => pitch of the solar field
    """
    def __init__(self,eff_opt_norm,iam_file,azimuth_field,roll_field,pitch):
        self.eff_opt_norm = eff_opt_norm
        self.iam_file = iam_file
        self.azimuth_field = azimuth_field
        self.roll_field = roll_field
        self.pitch = pitch

    def get_inc(self, step=None):
        """
        Returns the incidence angle [deg]
        """
        theta_long = 0.5*step #Dummy eq -- change
        theta_trans = 1*step #Dummy eq -- change
        return [theta_long,theta_trans]

    def get_IAM(self,theta_long,theta_trans):
        """
        Returns the IAM obtained as IAM = IAM_long(theta_long) * IAM_trans(theta_trans)  [-]
        """
        IAMs_df=pd.read_csv(self.iam_file)
        
        # Los IAMs están disponibles para valores de angulo que van de 5º en 5º. Es necesario interpolar el resultado
        theta_id=[int(round(theta_long/5,0)),int(round(theta_trans/5,0))]
        theta_diff=[theta_long-(theta_id[0])*5,theta_trans-(theta_id[1])*5]
        iam=[]
        
        for i in range(0,len(theta_diff)):
            
            if theta_diff[i]<0:     # Hemos redondeado hacia arriba, interpolamos con el valor actual y el anterior
                a=IAMs_df.iloc[theta_id[i],i+2]
                b=IAMs_df.iloc[theta_id[i]-1,i+2]
                iam.append(a+((a-b)/5)*theta_diff[i])
            
            elif theta_diff[i]>0:   # Hemos redondeado hacia abajo, interpolamos con el valor actual y el siguiente
                a=IAMs_df.iloc[theta_id[i],i+2]
                b=IAMs_df.iloc[theta_id[i]+1,i+2]
                iam.append(a+((b-a)/5)*theta_diff[i])
            
            elif theta_diff[i]==0:
                iam.append(IAMs_df.iloc[theta_id[i],i+2])
        
        product=iam[0]*iam[1] 
        iam.append(product)         # iam = [iam_long, iam_transv, iam_long*iam_transv]
        return iam
    
    def get_optic_eff(self,theta_long,theta_trans):
        """
        Returns the optic efficiency at one specific time step
        """
        iam = self.iam_file * theta_long * theta_trans #Dummy eq -- change
        return self.eff_opt_norm*iam

class Collector(Element,FresnelOptics):
    """
    Super class for every collector. This is the base class
    for all the other implemenation of collectors.
    """
    rho_optic = 0.5883  # [-]
    nu_1 = 0.0783  # [W/(m^2 K)]
    nu_2 = 0.003163  # [W/(m^2 K^2)]
    mdot_test = 0.0308  # [kg/sm2]

if __name__ == "__main__":
    optic = FresnelOptics(67.56,45)
