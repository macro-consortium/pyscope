import time

import pytest


def test_move(device, disconnect):
    device.Move(20000)
    while device.IsMoving:
        time.sleep(0.1)
    if device.Absolute:
        assert device.Position == 20000


def test_halt(device, disconnect):
    device.Move(20000)
    time.sleep(0.1)
    device.Halt()


def test_maxincrement(device, disconnect):
    assert device.MaxIncrement is not None


def test_maxstep(device, disconnect):
    assert device.MaxStep is not None


def test_stepsize(device, disconnect):
    assert device.StepSize is not None


def test_tempcomp(device, disconnect):
    if device.TempCompAvailable:
        assert device.TempComp is not None
        device.TempComp = True
        assert device.TempComp is True
        device.TempComp = False
        assert device.TempComp is False


def test_temperature(device, disconnect):
    assert device.Temperature is not None
