import pytest


def test_getswitchdescription(device, disconnect):
    for i in range(device.MaxSwitch):
        assert device.GetSwitchDescription(i) is not None


def test_getswitchname(device, disconnect):
    for i in range(device.MaxSwitch):
        assert device.GetSwitchName(i) is not None


def test_setswitchname(device, disconnect):
    for i in range(device.MaxSwitch):
        device.SetSwitchName(i, "test")


def test_setswitch(device, disconnect):
    for i in range(device.MaxSwitch):
        if device.CanWrite(i):
            device.SetSwitch(i, True)
            assert device.GetSwitch(i)
        else:
            assert device.GetSwitch(i) is not None


@pytest.mark.skip(reason="Not implemented")
def test_setswitchvalue(device, disconnect):
    for i in range(device.MaxSwitch):
        for j in range(
            device.MinSwitchValue(i),
            device.MaxSwitchValue(i) + 1,
            device.SwitchStep(i),
        ):
            if device.CanWrite(i):
                device.SetSwitchValue(i, j)
                assert device.GetSwitchValue(i) == j
            else:
                assert device.GetSwitchValue(i) is not None
