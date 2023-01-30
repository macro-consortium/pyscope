"""
Methods for finding various directory paths in iota
"""

import os.path

def iotalib_dir():
    "Return the absolute path to the 'iotalib' directory"
    # Assumes this module lives in the iotalib directory
    return os.path.dirname(os.path.abspath(__file__))

def iota_home():
    "Return the absolute path to the top-level 'iota' directory"
    return os.path.abspath(os.path.join(iotalib_dir(), ".."))

def image_dir():
    return os.path.join(iota_home(), "images")

def log_dir():
    return os.path.join(iota_home(), "logs")

def config_path(filename=None):
    """
    Return the path to the directory where config files are stored.
    If a filename is specified, include that filename at the end of the path.
    """
    path = os.path.join(iota_home(), "config")
    if filename is not None:
        path = os.path.join(path, filename)
    return path

def telrun_sls_path(filename=None):
    """
    Return the path to the directory where telrun.sls files are stored.
    If a filename is specified, include that filename at the end of the path.
    """

    path = os.path.join(iota_home(), "schedules")
    if filename is not None:
        path = os.path.join(path, filename)
    return path

def putty_path(filename=None):
    """
    Return the absolute path to the directory where the PuTTY distribution is stored.
    If a filename is specified, include that filename at the end of the path.
    """
    path = os.path.join(iota_home(), "putty")
    if filename is not None:
        path = os.path.join(path, filename)
    return path
    
def talon_wcs_path(filename=None):
    """
    Return the absolute path to the directory where the Talon WCS distribution
    is stored.
    If a filename is specified, include that filename at the end of the path.
    """

    path = os.path.join(iota_home(), "wcs")
    if filename is not None:
        path = os.path.join(path, filename)
    return path

