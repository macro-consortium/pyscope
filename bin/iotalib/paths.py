"""
Methods for finding various directory paths in iota
"""

import os.path

def iotalib_dir():
    # Assumes this module lives in the iotalib directory
    return os.path.dirname(os.path.abspath(__file__))

def iota_home():
    two_levels_up = os.path.join("..", "..")

    return os.path.abspath(os.path.join(iotalib_dir(), two_levels_up))

def image_dir():
    return os.path.join(iota_home(), "images")

def log_dir():
    return os.path.join(iota_home(), "logs")
