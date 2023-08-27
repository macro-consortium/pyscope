import numpy as np

from pyscope.utils import airmass


def test_airmass():
    deg = np.pi / 180
    assert np.round(airmass(90 * deg), 2) == 1.0
    assert np.round(airmass(60 * deg), 2) == 1.15
    assert np.round(airmass(45 * deg), 2) == 1.41
    assert np.round(airmass(30 * deg), 2) == 1.99
    assert np.round(airmass(15 * deg), 2) == 3.81
    assert np.round(airmass(0 * deg), 2) == 38.75
