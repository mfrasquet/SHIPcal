"""
This file contains the classes that define the collector in
shipcal
"""

from shipcal.elements import Element

class FresnelOptics():
    """
    Class for the optics in Linear Fresnel collectors.
    eff_opt_norm => Optical efficiency at normal incidence in % [float]
    iam_file => IAM file for the collector [csv]
    """
    def __init__(self,eff_opt_norm,iam_file):
        self.eff_opt_norm = eff_opt_norm
        self.iam_file = iam_file

class Collector(Element):
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
