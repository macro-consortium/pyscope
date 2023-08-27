import platform

import pytest

from pyscope.observatory import (
    ASCOMCamera,
    ASCOMCoverCalibrator,
    ASCOMDome,
    ASCOMDriver,
    ASCOMFilterWheel,
    ASCOMFocuser,
    ASCOMObservingConditions,
    ASCOMRotator,
    ASCOMSafetyMonitor,
    ASCOMSwitch,
    ASCOMTelescope,
    Camera,
    CoverCalibrator,
    Dome,
    Driver,
    FilterWheel,
    Focuser,
    ObservingConditions,
    Rotator,
    SafetyMonitor,
    Switch,
    Telescope,
)
from pyscope.observatory._docstring_inheritee import _DocstringInheritee


class TestASCOMDriver:
    def test_meta(self):
        assert type(ASCOMDriver) is _DocstringInheritee

    def test_parents(self):
        assert issubclass(ASCOMDriver, Driver)

    def test_multiplatform(self):
        if platform.system() == "Windows":
            assert ASCOMDriver("")._com_object is not None
        else:
            assert ASCOMDriver("")._com_object is None


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
        assert issubclass(cls_name, ASCOMDriver)

    def test_hardware_parent(self, cls_name):
        assert issubclass(cls_name, eval(cls_name.__name__.replace("ASCOM", "")))

    """def test_docstrings(self, cls_name):
        for name in cls_name.__dict__:
            if name != "__doc__":
                assert getattr(ASCOMDriver, name).__doc__ is not None"""
