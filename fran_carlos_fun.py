
from logging import exception
from shipcal import Weather  # , Collector, Consumer


def _is_coherent_weather() -> None:
    """
    This method will test if the instance of the Weather class is
    coherent with in the DNI and solar position. Available DNI when
    the sun is under the horizon is not acceptable.
    """
    self = Weather("src/shipcal/weather/data/Sevilla_Error.csv", step_resolution="10min")
    self.dni  # This is a pd.Series with the dni
    self.solar_elevation  # [°] Sun elevation from the astronomical horizon.

    # Aquí el reto es no usar for loops, tratar de usar el poder en paralelo
    # de pandas para que esta funcion consuma nada de tiempo incluso si
    # la resolución del Weather es muy alta.

    # Dummy index esto es el index que habrá que calcular si es que lo hay.
    datetime_index = self.dni.index[0]
    # Crear un error cuando el tmy no es coherente
    raise exception(
        "Incoherent Weather. There is non-zero DNI when sun is"
        f" under the horizon for the time {datetime_index}"
    )

    # Si el tmy no tiene errores hacer nada.


if __name__ == "__main__":
    _is_coherent_weather()
