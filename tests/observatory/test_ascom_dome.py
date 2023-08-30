import pytest


def test_abortslew(device, disconnect):
    device.AbortSlew()


def test_closeshutter(device, disconnect):
    if device.CanSetShutter:
        device.CloseShutter()


def test_findhome(device, disconnect):
    if device.CanFindHome:
        device.FindHome()


def test_openshutter(device, disconnect):
    if device.CanSetShutter:
        device.OpenShutter()


def test_park(device, disconnect):
    if device.CanPark:
        device.Park()


def test_setpark(device, disconnect):
    if device.CanSetPark:
        device.SetPark()


def test_slewtoaltitude(device, disconnect):
    if device.CanSetAltitude:
        device.SlewToAltitude(45)


def test_sletoazimuth(device, disconnect):
    if device.CanSetAzimuth:
        device.SlewToAzimuth(45)


def test_synctoazimuth(device, disconnect):
    if device.CanSyncAzimuth:
        device.SyncToAzimuth(45)


def test_altitude(device, disconnect):
    assert device.Altitude is not None


def test_athome(device, disconnect):
    assert device.AtHome is not None


def test_atpark(device, disconnect):
    if device.CanPark:
        assert device.AtPark is not None


def test_azimuth(device, disconnect):
    assert device.Azimuth == 45


def test_shutterstatus(device, disconnect):
    assert device.ShutterStatus is not None


def test_slaved(device, disconnect):
    if device.CanSlave:
        assert device.Slaved is not None


def test_slewing(device, disconnect):
    assert device.Slewing is not None
