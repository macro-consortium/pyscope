from pyscope._driver_utils import _import_driver

def Switch(driver_name, ascom=True):
    '''Return a switch object.

    Parameters
    ----------
    driver_name : str
        Name of the switch driver to use.
    ascom : bool
        If True, use the ASCOM driver.

    Returns
    -------
    switch : Switch
        Switch object.
    '''

    return _import_driver(driver_name, 'Switch', ascom=ascom)