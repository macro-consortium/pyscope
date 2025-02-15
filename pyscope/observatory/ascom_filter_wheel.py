import logging

from .ascom_device import ASCOMDevice
from .filter_wheel import FilterWheel

logger = logging.getLogger(__name__)


class ASCOMFilterWheel(ASCOMDevice, FilterWheel):
    def __init__(
        self, identifier, alpaca=False, device_number=0, protocol="http"
    ):
        """
        ASCOM implementation of the FilterWheel abstract base class.

        This class provides the functionality to control an ASCOM-compatible filter wheel device,
        including properties for focus offsets, filter names, and the current filter position.

        Parameters
        ----------
        identifier : `str`
            The unique device identifier. This can be the ProgID for COM devices or the device number for Alpaca devices.
        alpaca : `bool`, default : `False`, optional
            Whether the device is an Alpaca device.
        device_number : `int`, default : 0, optional
            The device number for Alpaca devices.
        protocol : `str`, default : "http", optional
            The communication protocol to use for Alpaca devices.
        """
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    @property
    def FocusOffsets(self):
        logger.debug(f"ASCOMFilterWheel.FocusOffsets property called")
        return self._device.FocusOffsets

    @property
    def Names(self):
        logger.debug(f"ASCOMFilterWheel.Names property called")
        return self._device.Names

    @property
    def Position(self):
        logger.debug(f"ASCOMFilterWheel.Position property called")
        return self._device.Position

    @Position.setter
    def Position(self, value):
        logger.debug(f"ASCOMFilterWheel.Position property set to {value}")
        self._device.Position = value
