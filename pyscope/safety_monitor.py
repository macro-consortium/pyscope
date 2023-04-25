from . import _import_driver

def SafetyMonitor(driver_name, ascom=True):
    '''Return a safety monitor object.

    Parameters
    ----------
    driver_name : str
        Name of the safety monitor driver to use.
    ascom : bool
        If True, use the ASCOM driver.

    Returns
    -------
    safety_monitor : SafetyMonitor
        Safety monitor object.
    '''

    return _import_driver(driver_name, 'SafetyMonitor', ascom=ascom)