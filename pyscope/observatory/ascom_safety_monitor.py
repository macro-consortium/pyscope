import logging

from .ascom_device import ASCOMDevice
from .safety_monitor import SafetyMonitor

logger = logging.getLogger(__name__)


class ASCOMSafetyMonitor(ASCOMDevice, SafetyMonitor):
    def __init__(
        self, identifier, alpaca=False, device_number=0, protocol="http"
    ):
        """
        ASCOM implementation of the SafetyMonitor base class.

        This class provides an interface to ASCOM-compatible safety monitors,
        allowing the observatory to check if weather, power, and other
        observatory-specific conditions allow safe usage of observatory equipment,
        such as opening the roof or dome.

        Parameters
        ----------
        identifier : `str`
            The device identifier.
        alpaca : `bool`, default : `False`, optional
            Whether the device is an Alpaca device.
        device_number : `int`, default : 0, optional
            The device number.
        protocol : `str`, default : "http", optional
            The device communication protocol.
        """
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    @property
    def IsSafe(self):
        logger.debug(f"ASCOMSafetyMonitor.IsSafe property called")
        return self._device.IsSafe
