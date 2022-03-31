"""
This file contains the classes that define the collector in
shipcal
"""

from shipcal.elements import Element

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
