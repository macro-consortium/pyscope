from pyscope._driver_utils import _import_driver

def Autofocus(driver_name):
    '''Return an autofocus object.

    Parameters
    ----------
    driver_name : str
        Name of the autofocus driver to use.

    Returns
    -------
    autofocus : Autofocus
        Autofocus object.
    '''

    return _import_driver(driver_name, 'Autofocus', ascom=False)