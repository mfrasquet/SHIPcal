"""
This file includes the base Element class, this inherits most of the
components of any simulation.
"""
from iapws import IAPWS97


def is_num(value):
    """ Returns if the instance is a number.

    Parameter
    ------------------------------
    Param1: value: type_description
       Returns true if the entry of the
       instance is an int, float number
        
    Returns: 
    -----------------------------
        false 
        type_description
    """

    if isinstance(value,(int,float)):
        return True
    else:
        return False


class Element:
    """ 
        This is the base class that inherits all SHIPCAL elements.
    """
    
    def __init__(self,P_bar=1,T_cel=30,h_kWh=''):
        """ 
        This method receives the imported attributes that 
        are found located in General_modules specifically 
        iapws97.py for perform two functions.
        
        Parameter
        ----------------------------------
         P_bar: (int, optional): type_description_. Defaults to 1.
            The parameter is used for funtion P_bar/10 where P_bar is pressure 
            
        T_cel: (int, optional): type_description_. Defaults to 30.
            The parameter is used for funtion T=T_cel + 273 where T_cel is celsius temperature
            
        h_kWh: (str, optional): type_description_. Defaults to ''.
            The parameter is used for funtion h=h_kWh * 3600 where h_kWh is kilowatt hour
        """
        if is_num(h_kWh):
            self._state_1_in = self._state_1_out = IAPWS97(P=P_bar/10, h=h_kWh * 3600 )
            self._state_2_in = self._state_2_out = self._state_1_in

        if is_num(T_cel):
            self._state_1_in = self._state_1_out = IAPWS97(P=P_bar/10, T=T_cel + 273)
            self._state_2_in = self._state_2_out = self._state_1_in

        try:
            self._state_1_in
        except Exception as error:
            raise ValueError("boundary condition init without T or h") from error

    # Primary 1
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
    def p_1_out(self):
        """ [ bar ] Pressure at the primary outlet of the element """
        return self._state_1_out.P * 10
    @p_1_out.setter
    def p_1_out(self, val):
        self._state_1_out = IAPWS97(P=val/10, T=self.t_1_out + 273)

    @property
    def m_dot_1_out(self):
        """ [ kg/s ] Massic fluid at the primary outlet of the element """
        return self._m_dot_1_out
    @m_dot_1_out.setter
    def m_dot_1_out(self, val):
        self._m_dot_1_out = val

    @property
    def x_1_out(self):
        """ [ % ] Steam quality of the state """
        return self._state_1_out.x
    @x_1_out.setter
    def x_1_out(self, val):
        self._state_1_out = IAPWS97(x=val, P=self.p_1_out/10)

    @property
    def t_1_out(self):
        """ [ C ] Temperature at the primary outlet of the element """
        return self._state_1_out.T - 273
    @t_1_out.setter
    def t_1_out(self, val):
        self._state_1_out = IAPWS97(P=self.p_1_out/10, T=val + 273)

    @property
    def h_1_out(self):
        """ [ kWh/kg ] Specific enthalpy at the primary outlet of the element """
        return self._state_1_out.h/3600
    @h_1_out.setter
    def h_1_out(self,val):
        self._state_1_out = IAPWS97(P=self.p_1_out/10, h=val)

    @property
    def s_1_out(self):
        """ [ kWh/kgK ] Specifi entropy at the primary outlet of the element """
        return self._state_1_out.s/3600
    @s_1_out.setter
    def s_1_out(self, val):
        self._state_1_out = IAPWS97(P=self.p_1_out/10, s=val)


    # Secondary 2
    # Inlet
    @property
    def p_2_in(self):
        """ [ bar ] Pressure at the secondary inlet of the element """
        return self._state_2_in.P * 10
    @p_2_in.setter
    def p_2_in(self, val):
        self._state_2_in = IAPWS97(P=val/10, T=self.t_2_in + 273)

    @property
    def m_dot_2_in(self):
        """ [ kg/s ] Massic fluid at the secondary inlet of the element """
        return self._m_dot_2_in
    @m_dot_2_in.setter
    def m_dot_2_in(self, val):
        self._m_dot_2_in = val

    @property
    def x_2_in(self):
        """ [ % ] Steam quality of the state """
        return self._state_2_in.x
    @x_2_in.setter
    def x_2_in(self, val):
        self._state_2_in = IAPWS97(x=val, P=self.p_2_in/10)

    @property
    def t_2_in(self):
        """ [ C ] Temperature at the secondary inlet of the element """
        return self._state_2_in.T - 273
    @t_2_in.setter
    def t_2_in(self, val):
        self._state_2_in = IAPWS97(P=self.p_2_in/10, T=val + 273)

    @property
    def h_2_in(self):
        """ [ kWh/kg ] Specific enthalpy at the secondary inlet of the element """
        return self._state_2_in.h/3600
    @h_2_in.setter
    def h_2_in(self,val):
        self._state_2_in = IAPWS97(P=self.p_2_in/10, h=val)

    @property
    def s_2_in(self):
        """ [ kWh/kgK ] Specifi entropy at the secondary inlet of the element """
        return self._state_2_in.s/3600
    @s_2_in.setter
    def s_2_in(self, val):
        self._state_2_in = IAPWS97(P=self.p_2_in/10, s=val)

    # Outlet
    @property
    def p_2_out(self):
        """ [ bar ] Pressure at the secondary outlet of the element """
        return self._state_2_out.P * 10
    @p_2_out.setter
    def p_2_out(self, val):
        self._state_2_out = IAPWS97(P=val/10, T=self.t_2_out + 273)

    @property
    def m_dot_2_out(self):
        """ [ kg/s ] Massic fluid at the secondary outlet of the element """
        return self._m_dot_2_out
    @m_dot_2_out.setter
    def m_dot_2_out(self, val):
        self._m_dot_2_out = val

    @property
    def x_2_out(self):
        """ [ % ] Steam quality of the state """
        return self._state_2_out.x
    @x_2_out.setter
    def x_2_out(self, val):
        self._state_2_out = IAPWS97(x=val, P=self.p_2_out/10)

    @property
    def t_2_out(self):
        """ [ C ] Temperature at the secondary outlet of the element """
        return self._state_2_out.T - 273
    @t_2_out.setter
    def t_2_out(self, val):
        self._state_2_out = IAPWS97(P=self.p_2_out/10, T=val + 273)

    @property
    def h_2_out(self):
        """ [ kWh/kg ] Specific enthalpy at the secondary outlet of the element """
        return self._state_2_out.h/3600
    @h_2_out.setter
    def h_2_out(self,val):
        self._state_2_out = IAPWS97(P=self.p_2_out/10, h=val)

    @property
    def s_2_out(self):
        """ [ kWh/kgK ] Specifi entropy at the secondary outlet of the element """
        return self._state_2_out.s/3600
    @s_2_out.setter
    def s_2_out(self, val):
        self._state_2_out = IAPWS97(P=self.p_2_out/10, s=val)

    # Thermal innertia


      
if __name__ == "__main__":
    test1 = Element(P_bar=1, T_cel=60)
    test1.p_1_in = 6
    test1.t_1_in = 60
    print(test1.h_1_in)
