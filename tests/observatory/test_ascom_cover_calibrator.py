import pytest


def test_calibratoron(device, disconnect):
    device.CalibratorOn(1)
    assert device.Brightness == 1
    device.CalibratorOff()


def test_calibratoroff(device, disconnect):
    device.CalibratorOn(1)
    device.CalibratorOff()
    assert device.Brightness == 0


def test_opencover(device, disconnect):
    device.OpenCover()
    assert device.CoverState == 2


def test_closecover(device, disconnect):
    device.OpenCover()
    device.CloseCover()
    assert device.CoverState == 2


def test_haltcover(device, disconnect):
    device.OpenCover()
    device.HaltCover()
    assert device.CoverState == 4


def test_calibratorstate(device, disconnect):
    device.CalibratorOn(1)
    assert device.CalibratorState == 2


def test_maxbrightness(device, disconnect):
    assert device.MaxBrightness is not None
