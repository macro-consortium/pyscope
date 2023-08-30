import logging

from .ascom_device import ASCOMDevice
from .safety_monitor import SafetyMonitor

logger = logging.getLogger(__name__)


class ASCOMSafetyMonitor(ASCOMDevice, SafetyMonitor):
    def __init__(self, identifier, alpaca=False, device_number=0, protocol="http"):
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    def Choose(self, SafetyMonitorID):
        logger.debug(f"ASCOMSafetyMonitor.Choose({SafetyMonitorID}) called")
        self._device.Choose(SafetyMonitorID)

    @property
    def IsSafe(self):
        logger.debug(f"ASCOMSafetyMonitor.IsSafe property called")
        return self._device.IsSafe
