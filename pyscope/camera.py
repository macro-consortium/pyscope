from pyscope._driver_utils import _import_driver

def Camera(driver_name, ascom=True):
    '''Return a camera object.

    Parameters
    ----------
    driver_name : str
        Name of the camera driver to use.
    ascom : bool
        If True, use the ASCOM driver.

    Returns
    -------
    camera : Camera
        Camera object.
    '''

    return _import_driver(driver_name, 'Camera', ascom=ascom)