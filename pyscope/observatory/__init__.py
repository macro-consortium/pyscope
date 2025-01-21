"""
The `observatory` module provides classes and functions for controlling and automating
observatory hardware and operations. This currently includes support only for the
`Robert L. Mutel Telescope` at the University of Iowa, but is designed to be extensible
to all motorized observatory telescopes in the future.
Operations include managing telescopes, cameras, focuser, filter wheels, domes, and other
devices commonly found in an observatory setup.
"""

# isort: skip_file

from .collect_calibration_set import collect_calibration_set
from .zwo_camera import ZWOCamera
from .pwi_autofocus import PWIAutofocus
from .observatory import Observatory
from .observatory_exception import ObservatoryException
from .simulator_server import SimulatorServer
from .pwi4_focuser import PWI4Focuser
from .pwi4_autofocus import PWI4Autofocus
from .maxim import Maxim
from .ip_cover_calibrator import IPCoverCalibrator
from .html_safety_monitor import HTMLSafetyMonitor
from .html_observing_conditions import HTMLObservingConditions
from .ascom_telescope import ASCOMTelescope
from .ascom_switch import ASCOMSwitch
from .ascom_safety_monitor import ASCOMSafetyMonitor
from .ascom_rotator import ASCOMRotator
from .ascom_observing_conditions import ASCOMObservingConditions
from .ascom_focuser import ASCOMFocuser
from .ascom_filter_wheel import ASCOMFilterWheel
from .ascom_dome import ASCOMDome
from .ascom_cover_calibrator import ASCOMCoverCalibrator
from .ascom_camera import ASCOMCamera
from .ascom_device import ASCOMDevice
from .telescope import Telescope
from .switch import Switch
from .safety_monitor import SafetyMonitor
from .rotator import Rotator
from .observing_conditions import ObservingConditions
from .focuser import Focuser
from .filter_wheel import FilterWheel
from .dome import Dome
from .cover_calibrator import CoverCalibrator
from .camera import Camera
from .autofocus import Autofocus
from .device import Device
from ._pwi4 import _PWI4
import logging

logger = logging.getLogger(__name__)


# from .skyx import SkyX


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
    "Rotator",
    "SafetyMonitor",
    "Switch",
    "Telescope",
    "collect_calibration_set",
    "SimulatorServer",
]
