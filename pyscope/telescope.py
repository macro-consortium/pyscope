from pyscope._driver_utils import _import_driver

def Telescope(driver_name, ascom=True):
    '''Return a telescope object.

    Parameters
    ----------
    driver_name : str
        Name of the telescope driver to use.
    ascom : bool
        If True, use the ASCOM driver.

    Returns
    -------
    telescope : Telescope
        Telescope object.
    '''

    return _import_driver(driver_name, 'Telescope', ascom=ascom)