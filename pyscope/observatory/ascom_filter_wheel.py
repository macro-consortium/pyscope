import logging

from .ascom_device import ASCOMDevice
from .filter_wheel import FilterWheel

logger = logging.getLogger(__name__)


class ASCOMFilterWheel(ASCOMDevice, FilterWheel):
    def __init__(self, identifier, alpaca=False, device_number=0, protocol="http"):
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    def Choose(self, FilterWheelID):
        logger.debug(f"ASCOMFilterWheel.Choose({FilterWheelID}) called")
        self._device.Choose(FilterWheelID)

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
