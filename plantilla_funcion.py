import numpy as np


def funcion_nombre_representativo(nombre_repr_inpt_1, nombre_repr_inpt_2):
    """
    _summary_

    Parameters
    ----------
    nombre_repr_inpt_1 : _type_
        _description_ (incluir unidades)
    nombre_repr_inpt_2 : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """

    nombre_repr_resultado = nombre_repr_inpt_1 * nombre_repr_inpt_2

    return nombre_repr_resultado


def interpolate_prop(self, h_id, prop_array):
    """
    Interpolate the property to a fractional index of the array

    Parameters
    ----------
    h_id : float
        Noninteger index
    prop_array : pd.Series
        Series of property to interpolate. Must have a datetime index.

    Returns
    -------
    float
        Interpolated property value at h_id.
    """
    h_floor = int(np.floor(h_id))
    h_ceil = int(np.ceil(h_id))
    h_change = h_ceil - h_floor
    if h_change == 0:
        return prop_array[h_floor]
    dprop = prop_array[h_ceil] - prop_array[h_floor]

    prop = prop_array[h_floor] + (dprop / h_change) * (h_id - h_floor)

    return prop
