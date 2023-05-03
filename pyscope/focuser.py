from pyscope._driver_utils import _import_driver

def Focuser(driver_name, ascom=True):
    '''Return a focuser object.

    Parameters
    ----------
    driver_name : str
        Name of the focuser driver to use.
    ascom : bool
        If True, use the ASCOM driver.

    Returns
    -------
    focuser : Focuser
        Focuser object.
    '''

    return _import_driver(driver_name, 'Focuser', ascom=ascom)