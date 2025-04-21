import time

import pytest


def test_halt(device, disconnect):
    device.Move(5)
    device.Halt()


def test_moveabsolute(device, disconnect):
    device.MoveAbsolute(5)
    while device.IsMoving:
        time.sleep(0.1)


def test_movemechanical(device, disconnect):
    device.MoveMechanical(5)
    while device.IsMoving:
        time.sleep(0.1)


def test_sync(device, disconnect):
    device.Sync(5)


def test_position(device, disconnect):
    assert device.Position is not None


def test_reverse(device, disconnect):
    if device.CanReverse:
        device.Reverse = True
        assert device.Reverse
        device.Reverse = False
        assert device.Reverse == False


def test_mechanicalposition(device, disconnect):
    assert device.MechanicalPosition is not None


def test_stepsize(device, disconnect):
    assert device.StepSize is not None


def test_targetposition(device, disconnect):
    device.Move(5)
    while device.IsMoving:
        time.sleep(0.1)
    device.Move(5)
    assert device.TargetPosition == 15
