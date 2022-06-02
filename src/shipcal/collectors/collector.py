"""
This file contains the classes that define the collector in
shipcal
"""
from pathlib import Path

import pkg_resources
import pandas as pd

from shipcal.elements import Element


class Collector(Element):
    """
    Super class for every collector. This is the base class
    for all the other implemenation of collectors.
    eff_opt_norm => Optical efficiency at normal incidence [-]
    iam_file => IAM file for the collector [csv]
    azimuth_field => azimuth of the solar field [deg]
    roll_field => roll of the solar field [deg]
    pitch_field => pitch of the solar field
    """

    def __init__(
        self, eff_opt_norm, nu_1, nu_2, mdot_test, aperture_area,
        iam_file=None,
        azimuth_field=0, roll_field=0, pitch_field=0
    ):
        Element.__init__(self)

        self.eff_opt_norm = eff_opt_norm
        self.nu_1 = nu_1
        self.nu_2 = nu_2
        self.mdot_test = mdot_test
        self.aperture_area = aperture_area

        self.iam_file = iam_file

        self.azimuth_field = azimuth_field
        self.roll_field = roll_field
        self.pitch_field = pitch_field

    @property
    def eff_opt_norm(self):
        """
        [-] Maximum optical efficiency of the collector. This value must
        be between 0 and 1.
        """
        return self._eff_opt_norm

    @eff_opt_norm.setter
    def eff_opt_norm(self, val):
        self._eff_opt_norm = val

    @property
    def nu_1(self):
        """
        [W/(m^2 K)] The linear term in the energy losses equation.
        """
        return self._nu_1

    @nu_1.setter
    def nu_1(self, val):
        self._nu_1 = val

    @property
    def nu_2(self):
        """
        [W/(m^2 K^2)] The quadratic term in the energy losses equation.
        """
        return self._nu_2

    @nu_2.setter
    def nu_2(self, val):
        self._nu_2 = val

    @property
    def mdot_test(self):
        """
        [kg/sm2] Massic fluid used in the tests to obtain the module
        characteristics
        """
        return self._mdot_test

    @mdot_test.setter
    def mdot_test(self, val):
        self._mdot_test = val

    @property
    def aperture_area(self):
        """
        [m^2] Total area that could collect solar energy
        """
        return self._aperture_area

    @aperture_area.setter
    def aperture_area(self, val):
        self._aperture_area = val

    @property
    def azimuth_field(self):
        """
        [°] Azimuth orientation of the solar field
        """
        return self._azimuth_field

    @azimuth_field.setter
    def azimuth_field(self, val):
        self._azimuth_field = val

    @property
    def roll_field(self):
        """
        [°] Roll orientation of the solar field
        """
        return self._roll_field

    @roll_field.setter
    def roll_field(self, val):
        self._roll_field = val

    @property
    def pitch_field(self):
        """
        [°] Pitch orientation of the solar field
        """
        return self._pitch

    @pitch_field.setter
    def pitch_field(self, val):
        self._pitch = val

    @property
    def iam_file(self):
        """
        Location of the IAM file table of values. The file must have the
        following format:

        Angle deg,Incidence angle rad,IAM_long,IAM_transv
        0,0,1,1.01
        5,0.0872,0.9924,0.998

        This is one line per equally spaced angle with its IAM values
        """
        return self._iam_file

    @iam_file.setter
    def iam_file(self, path_to_file):
        if path_to_file is None:
            self._iam_file = Path(
                pkg_resources.resource_filename("shipcal.collectors", "data/SOLATOM_real.csv")
            )
        else:
            self._iam_file = Path(path_to_file)
            if not self._iam_file.exists():
                raise ValueError(f"No such IAM file {path_to_file}.")

    def get_iam(self, theta_long=0, theta_trans=0):
        """
        Obtains the IAM longitudinal, transversal, and its product
        obtained as IAM = IAM_long(theta_long) * IAM_trans(theta_trans) [-]
        from the longitudinal and transversal angles measured in degrees
        from the normal to the collector plane. The values are obtained
        from interpolating the vaues in the provided iam_file.

        Parameters
        ----------
        theta_long : float
            [°] Longitudinal incidence angle. Measured from the collector
            normal in the direction parallel to the longest side of the
            collector.
        theta_trans : float
            [°] Transversal incidence angle. Measured from the collector
            normal in the direction perpendicular to the longest side of the
            collector.

        Returns
        -------
        iams : List
            Returns a list of the IAMs; long, trans and its product
            IAM_long*IAM*trans. [IAM_long, IAM_trans, IAM]
        """
        IAMs_df = pd.read_csv(self.iam_file)

        # IAMs are available fot angle values ranging from 5º to 5º,
        # it is necessary to interpolate the result
        theta_id = [int(round(theta_long / 5, 0)), int(round(theta_trans / 5, 0))]
        theta_diff = [theta_long - (theta_id[0]) * 5, theta_trans - (theta_id[1]) * 5]
        iams = []

        for i in range(0, len(theta_diff)):
            # It has been rounded up, it is necessary to interpolate
            # with the current value and the previous one
            if theta_diff[i] < 0:
                a = IAMs_df.iloc[theta_id[i], i + 2]
                b = IAMs_df.iloc[theta_id[i] - 1, i + 2]
                iams.append(a + ((a - b) / 5) * theta_diff[i])
            # It has been rounded down, it is necessary to interpolate
            # with the current value and the next one
            elif theta_diff[i] > 0:
                a = IAMs_df.iloc[theta_id[i], i + 2]
                b = IAMs_df.iloc[theta_id[i] + 1, i + 2]
                iams.append(a + ((b - a) / 5) * theta_diff[i])
            elif theta_diff[i] == 0:
                iams.append(IAMs_df.iloc[theta_id[i], i + 2])
        product = iams[0] * iams[1]
        # iams = [iam_long, iam_transv, iam_long*iam_transv]
        iams.append(product)
        return iams

    # Check
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
        
        [theta_long, theta_trans] = self.get_incidence_angle(step)
        energy_gain = weather.dni[step] * self.aperture_area\
            * self.get_optic_eff(theta_long, theta_trans)
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

    def get_incidence_angle(self, step, weather):
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
        return self.eff_opt_norm * self.get_iam(theta_long, theta_trans)[-1]


if __name__ == "__main__":
    pass
