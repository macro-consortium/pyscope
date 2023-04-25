from . import _import_driver

def FilterWheel(driver_name, ascom=True):
    '''Return a filter wheel object.

    Parameters
    ----------
    driver_name : str
        Name of the filter wheel driver to use.
    ascom : bool
        If True, use the ASCOM driver.

    Returns
    -------
    filter_wheel : FilterWheel
        Filter wheel object.
    '''

    return _import_driver(driver_name, 'FilterWheel', ascom=ascom)