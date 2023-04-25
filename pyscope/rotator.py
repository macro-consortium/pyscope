from . import _import_driver

def Rotator(driver_name, ascom=True):
    '''Return a rotator object.

    Parameters
    ----------
    driver_name : str
        Name of the rotator driver to use.
    ascom : bool
        If True, use the ASCOM driver.

    Returns
    -------
    rotator : Rotator
        Rotator object.
    '''

    return _import_driver(driver_name, 'Rotator', ascom=ascom)