"""
This file includes the base Element class, this inherits most of the
components of any simulation.
"""
from iapws import IAPWS97

def is_num(value):
    """ returns if the instance is a number. !! check if there is an
    already built function for this """

    if isinstance(value,(int,float)):
        return True
    else:
        return False

class Element:
    """
    Base class inherits every other element in SHIPcal.
    """

    def __init__(self,P_bar=1,T_cel=30,h_kWh=''):
        if is_num(h_kWh):
            self._state_1_in=IAPWS97(P=P_bar/10, h=h_kWh * 3600 )
        if is_num(T_cel):
            self._state_1_in=IAPWS97(P=P_bar/10, T=T_cel + 273)
        try:
            self._state_1_in
        except:
            raise ValueError("boundary condition init without T or h")

    # Primary
    # Inlet
    @property
    def p_1_in(self):
        """ [ bar ] Pressure at the primary inlet of the element """
        return self._state_1_in.P * 10
    @p_1_in.setter
    def p_1_in(self, val):
        self._state_1_in = IAPWS97(P=val/10, T=self.t_1_in + 273)

    @property
    def m_dot_1_in(self):
        """ [ kg/s ] Massic fluid at the primary inlet of the element """
        return self._m_dot_1_in
    @m_dot_1_in.setter
    def m_dot_1_in(self, val):
        self._m_dot_1_in = val
    
    @property
    def x_1_in(self):
        """ [ % ] Steam quality of the state """
        return self._state_1_in.x
    @x_1_in.setter
    def x_1_in(self, val):
        self._state_1_in = IAPWS97(x=val, P=self.p_1_in/10)

    @property
    def t_1_in(self):
        """ [ C ] Temperature at the primary inlet of the element """
        return self._state_1_in.T - 273
    @t_1_in.setter
    def t_1_in(self, val):
        self._state_1_in = IAPWS97(P=self.p_1_in/10, T=val + 273)

    @property
    def h_1_in(self):
        """ [ kWh/kg ] Specific enthalpy at the primary inlet of the element """
        return self._state_1_in.h/3600
    @h_1_in.setter
    def h_1_in(self,val):
        self._state_1_in = IAPWS97(P=self.p_1_in/10, h=val)

    @property
    def s_1_in(self):
        """ [ kWh/kgK ] Specifi entropy at the primary inlet of the element """
        return self._state_1_in.s/3600
    @s_1_in.setter
    def s_1_in(self, val):
        self._state_1_in = IAPWS97(P=self.p_1_in/10, s=val)

    # Outlet
    @property
    def pressure_1_out(self):
        """ [ bar ] Pressure at the primary outlet of the element """
        return self._pressure_1_out
    @pressure_1_out.setter
    def pressure_1_out(self, val):
        self._pressure_1_out = val

    @property
    def m_dot_1_out(self):
        """ [ kg/s ] Massic fluid at the primary outlet of the element """
        return self._m_dot_1_out
    @m_dot_1_out.setter
    def m_dot_1_out(self, val):
        self._m_dot_1_out = val

    @property
    def temp_1_out(self):
        """ [ C ] Temperature at the primary outlet of the element """
        return self._temp_1_out
    @temp_1_out.setter
    def temp_1_out(self, val):
        self._temp_1_out = val

    @property
    def h_1_out(self):
        """ [ kWh ] Enthalpy at the primary outlet of the element """
        return self._h_1_out
    @h_1_out.setter
    def h_1_out(self, val):
        self._h_1_out = val

    @property
    def s_1_out(self):
        """ [ kWh ] Entropy at the primary outlet of the element """
        return self._s_1_out
    @s_1_out.setter
    def s_1_out(self, val):
        self._s_1_out = val


    # Secondary
    # Inlet
    @property
    def pressure_s_in(self):
        """ [ bar ] Pressure at the secondary inlet of the element """
        return self._pressure_s_in
    @pressure_s_in.setter
    def pressure_s_in(self, val):
        self._pressure_s_in=val

    @property
    def m_dot_s_in(self):
        """ [ kg/s ] Massic fluid at the secondary inlet of the element """
        return self._m_dot_s_in
    @m_dot_s_in.setter
    def m_dot_s_in(self, val):
        self._m_dot_s_in=val

    @property
    def temp_s_in(self):
        """ [ C ] Temperature at the secondary inlet of the element """
        return self._temp_s_in
    @temp_s_in.setter
    def temp_s_in(self, val):
        self._temp_s_in=val

    @property
    def h_s_in(self):
        """ [ kWh ] Enthalpy at the secondary inlet of the element """
        return self._h_s_in
    @h_s_in.setter
    def h_s_in(self, val):
        self._h_s_in=val

    @property
    def s_s_in(self):
        """ [ kWh ] Entropy at the secondary inlet of the element """
        return self._s_s_in
    @s_s_in.setter
    def s_s_in(self, val):
        self._s_s_in=val

    # Outlet
    @property
    def pressure_s_out(self):
        """ [ bar ] Pressure at the secondary outlet of the element """
        return self._pressure_s_out
    @pressure_s_out.setter
    def pressure_s_out(self, val):
        self._pressure_s_out = val

    @property
    def m_dot_s_out(self):
        """ [ kg/s ] Massic fluid at the secondary outlet of the element """
        return self._m_dot_s_out
    @m_dot_s_out.setter
    def m_dot_s_out(self, val):
        self._m_dot_s_out = val

    @property
    def temp_s_out(self):
        """ [ C ] Temperature at the secondary outlet of the element """
        return self._temp_s_out
    @temp_s_out.setter
    def temp_s_out(self, val):
        self._temp_s_out = val

    @property
    def h_s_out(self):
        """ [ kWh ] Enthalpy at the secondary outlet of the element """
        return self._h_s_out
    @h_s_out.setter
    def h_s_out(self, val):
        self._h_s_out = val

    @property
    def s_s_out(self):
        """ [ kWh ] Entropy at the secondary outlet of the element """
        return self._s_s_out
    @s_s_out.setter
    def s_s_out(self, val):
        self._s_s_out = val


    # Thermal innertia

test1 = Element(P_bar=1,T_cel=60)
test1.p_1_in=6
test1.t_1_in=60
print(test1.h_1_in)
