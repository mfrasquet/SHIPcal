from elements import Element

class Collector(Element):
    """
    Super class for every collector. This is the base class
    for all the other implemenation of collectors.
    """
    rho_optic = 0.5883 # [-]
    nu_1 = 0.0783 # [W/(m^2 K)]
    nu_2 = 0.003163 # [W/(m^2 K^2)]
    mdot_test = 0.0308 # [kg/sm2]