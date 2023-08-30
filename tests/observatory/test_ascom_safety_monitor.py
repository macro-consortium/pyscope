import pytest

from pyscope.observatory import ASCOMSafetyMonitor


def test_issafe(device, disconnect):
    assert device.IsSafe is not None
