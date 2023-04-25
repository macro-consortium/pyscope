from . import _import_driver

def ObservingConditions(driver_name, ascom=True):
    '''Return an observing conditions object.

    Parameters
    ----------
    driver_name : str
        Name of the observing conditions driver to use.
    ascom : bool
        If True, use the ASCOM driver.

    Returns
    -------
    observing_conditions : ObservingConditions
        Observing conditions object.
    '''

    return _import_driver(driver_name, 'ObservingConditions', ascom=ascom)