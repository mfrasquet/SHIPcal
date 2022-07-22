from shipcal.collectors import Collector
from shipcal import Weather


def get_energy_thermal_loss(weather: Weather, step: int) -> float:
    """
    This function considers the thermal losses for a Plane collector

    Parameters
    ----------
    weather : Weather
        Object that contains the weather data.
    step : int
        Current simulation step.

    Returns
    -------
    float
        Energy loss in the current step moment
    """
    # Parameters that define the Collector
    self = Collector(
        eff_opt_norm=0.68,
        nu_1=0.043,
        nu_2=0.0010,
        mdot_test=0.5,
        aperture_area=13
        # azimuth_field=0, roll_field=0, pitch_field=0
        # iam_file=pkg_resources.resource_filename(
        #     "shipcal.collectors", "data/SOLATOM_real.csv"
        # ),  # defuault
    )

    # Your code here
    x, y = self.nu_1, self.nu_2
    loss = x**2 + y**2
    # Your code here

    return loss


if __name__ == "__main__":
    sevilla_file = "./src/shipcal/weather/data/Sevilla.csv"
    weather = Weather(sevilla_file)
    # First midday of the year
    step = 12
    energy_loss = get_energy_thermal_loss(weather, step)
