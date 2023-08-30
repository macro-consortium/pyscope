import pytest

from pyscope.observatory import (
    ASCOMCamera,
    ASCOMCoverCalibrator,
    ASCOMDevice,
    ASCOMDome,
    ASCOMFilterWheel,
    ASCOMFocuser,
    ASCOMObservingConditions,
    ASCOMRotator,
    ASCOMSafetyMonitor,
    ASCOMSwitch,
    ASCOMTelescope,
    Camera,
    CoverCalibrator,
    Device,
    Dome,
    FilterWheel,
    Focuser,
    ObservingConditions,
    Rotator,
    SafetyMonitor,
    SimulatorServer,
    Switch,
    Telescope,
)
from pyscope.observatory._docstring_inheritee import _DocstringInheritee


class TestASCOMDriver:
    def test_meta(self):
        assert type(ASCOMDevice) is _DocstringInheritee

    def test_parents(self):
        assert issubclass(ASCOMDevice, Device)


@pytest.mark.parametrize(
    "cls_name",
    [
        ASCOMCamera,
        ASCOMCoverCalibrator,
        ASCOMDome,
        ASCOMFilterWheel,
        ASCOMFocuser,
        ASCOMObservingConditions,
        ASCOMRotator,
        ASCOMSafetyMonitor,
        ASCOMSwitch,
        ASCOMTelescope,
    ],
)
class TestAllASCOMClasses:
    def test_meta(self, cls_name):
        assert type(cls_name) is _DocstringInheritee

    def test_driver_parent(self, cls_name):
        assert issubclass(cls_name, ASCOMDevice)

    def test_hardware_parent(self, cls_name):
        assert issubclass(cls_name, eval(cls_name.__name__.replace("ASCOM", "")))

    """def test_docstrings(self, cls_name):
        for name in cls_name.__dict__:
            if name != "__doc__":
                assert getattr(ASCOMDevice, name).__doc__ is not None"""
