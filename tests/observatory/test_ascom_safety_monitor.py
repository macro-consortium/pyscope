import pytest


def test_issafe(device, disconnect):
    assert device.IsSafe is not None
