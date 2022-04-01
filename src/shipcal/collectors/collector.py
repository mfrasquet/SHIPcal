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
    def __init__(self, eff_opt_norm, iam_file, azimuth_field, roll_field, pitch):
        self.eff_opt_norm = eff_opt_norm
        self.iam_file = iam_file
        self.azimuth_field = azimuth_field
        self.roll_field = roll_field
        self.pitch = pitch

    def get_incidence_angle(self, step=None):
        """
        Returns the incidence angle [deg]
        """
        theta_long = 0.5 * step  # Dummy eq -- change
        theta_trans = 1 * step  # Dummy eq -- change
        return [theta_long, theta_trans]

    def get_optic_eff(self, theta_long, theta_trans):
        """
        Returns the optic efficiency at one specific time step
        """
        iam = self.iam_file * theta_long * theta_trans  # Dummy eq -- change
        return self.eff_opt_norm * iam


class Collector(Element, FresnelOptics):
    """
    Super class for every collector. This is the base class
    for all the other implemenation of collectors.

    Parameters
    ----------
    Element : _type_
        _description_
    FresnelOptics : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    rho_optic = 0.5883  # [-]
    nu_1 = 0.0783  # [W/(m^2 K)]
    nu_2 = 0.003163  # [W/(m^2 K^2)]
    mdot_test = 0.0308  # [kg/sm2]
    aperture_area = 13.14  # [m^2]

    def __init__(
        self, eff_opt_norm, iam_file, azimuth_field, roll_field, pitch,
        P_bar=1, T_cel=30, h_kWh=''
    ):
        Element.__init__(P_bar, T_cel, h_kWh)
        FresnelOptics.__init__(
            eff_opt_norm, iam_file, azimuth_field, roll_field, pitch
        )

    def get_energy_gain(self, step, weather):
        """
        Returns the maximum energy that the collector could win in the
        currrent step with the weather in the same step.

        Parameters
        ----------
        step : int
            Simulation step.
        weather : Weather
            Location weather, must be a Weather instance.

        Returns
        -------
        energy_gain : float
            Maximum energy that the collector could obtain. Energy before losses
        """
        energy_gain = weather.dni[step] * self.aperture_area\
            * self.get_optic_eff(self.get_incidence_angle(step))
        return energy_gain

    def get_energy_losses(self, step, weather):
        """
        Obtain the energy that the collector will loss to the environment.
        Later, this result should be substracted from the energy gain.

        Parameters
        ----------
        step : int
            Simulation step.
        weather : Weather
            Location weather, must be a Weather instance.

        Returns
        -------
        energy_loss : float
            Energy that will be radiated to the surroundings.
        """
        energy_loss = 15
        return energy_loss

    def operation(self, step, weather):
        """
        Computes the operation state based in the thermodinamic state
        and the weather. This method should be used to update the
        thermodinamic state and obtain the produced energy.

        Parameters
        ----------
        step : int
            Simulation step.
        weather : Weather
            Location weather, must be a Weather instance.

        Returns
        -------
        produced_energy : float
            Energy after losses.
        """
        produced_energy = self.get_energy_gain(step, weather) \
            - self.get_energy_losses(step, weather)
        return produced_energy


if __name__ == "__main__":
    optic = FresnelOptics(67.56, 45)
