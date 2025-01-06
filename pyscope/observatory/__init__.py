"""
The `observatory` module provides classes and functions for controlling and automating
observatory hardware and operations. This currently includes support only for the
`Robert L. Mutel Telescope` at the University of Iowa, but is designed to be extensible
to all motorized observatory telescopes in the future.
Operations include managing telescopes, cameras, focuser, filter wheels, domes, and other
devices commonly found in an observatory setup.
"""

# isort: skip_file

import logging

logger = logging.getLogger(__name__)

from ._docstring_inheritee import _DocstringInheritee
from ._pwi4 import _PWI4

from .device import Device

from .autofocus import Autofocus
from .camera import Camera
from .cover_calibrator import CoverCalibrator
from .dome import Dome
from .filter_wheel import FilterWheel
from .focuser import Focuser
from .observing_conditions import ObservingConditions
from .rotator import Rotator
from .safety_monitor import SafetyMonitor
from .switch import Switch
from .telescope import Telescope

from .ascom_device import ASCOMDevice
from .ascom_camera import ASCOMCamera
from .ascom_cover_calibrator import ASCOMCoverCalibrator
from .ascom_dome import ASCOMDome
from .ascom_filter_wheel import ASCOMFilterWheel
from .ascom_focuser import ASCOMFocuser
from .ascom_observing_conditions import ASCOMObservingConditions
from .ascom_rotator import ASCOMRotator
from .ascom_safety_monitor import ASCOMSafetyMonitor
from .ascom_switch import ASCOMSwitch
from .ascom_telescope import ASCOMTelescope

from .html_observing_conditions import HTMLObservingConditions
from .html_safety_monitor import HTMLSafetyMonitor
from .ip_cover_calibrator import IPCoverCalibrator
from .maxim import Maxim
from .pwi4_autofocus import PWI4Autofocus
from .pwi4_focuser import PWI4Focuser

from .simulator_server import SimulatorServer

from .observatory_exception import ObservatoryException
from .observatory import Observatory

from .pwi_autofocus import PWIAutofocus

from .zwo_camera import ZWOCamera

from .reconfig import ReconfigConfigs

# from .skyx import SkyX

from .collect_calibration_set import collect_calibration_set

__all__ = [
    "ASCOMCamera",
    "ASCOMCoverCalibrator",
    "ASCOMDevice",
    "ASCOMDome",
    "ASCOMFilterWheel",
    "ASCOMFocuser",
    "ASCOMObservingConditions",
    "ASCOMRotator",
    "ASCOMSwitch",
    "ASCOMTelescope",
    "Autofocus",
    "Camera",
    "CoverCalibrator",
    "Device",
    "Dome",
    "FilterWheel",
    "Focuser",
    "HTMLObservingConditions",
    "HTMLSafetyMonitor",
    "IPCoverCalibrator",
    "Maxim",
    "ObservatoryException",
    "Observatory",
    "ObservingConditions",
    "PWI4Autofocus",
    "PWI4Focuser",
    "PWIAutofocus",
    "ReconfigConfigs",
    "Rotator",
    "SafetyMonitor",
    "Switch",
    "Telescope",
    "collect_calibration_set",
    "SimulatorServer",
    "ZWOCamera",
]
