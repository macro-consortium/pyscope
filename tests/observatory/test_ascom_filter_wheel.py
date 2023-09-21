import pytest


def test_focusoffsets(device, disconnect):
    assert device.FocusOffsets is not None


def test_names(device, disconnect):
    assert device.Names is not None


def test_position(device, disconnect):
    assert device.Position is not None
