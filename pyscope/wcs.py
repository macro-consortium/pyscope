from . import _import_driver

def WCS(driver_name):
    '''Return a WCS object.

    Parameters
    ----------
    driver_name : str
        Name of the WCS driver to use.

    Returns
    -------
    WCS : WCS
        WCS object.
    '''

    return _import_driver(driver_name, 'WCS', ascom=False)