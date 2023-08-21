import logging
from .filter_wheel import FilterWheel

logger = logging.getLogger(__name__)


class ASCOMFilterWheel(FilterWheel):
    def Choose(self, FilterWheelID):
        logger.debug(f"ASCOMFilterWheel.Choose({FilterWheelID}) called")
        self._com_object.Choose(FilterWheelID)

    @property
    def FocusOffsets(self):
        logger.debug(f"ASCOMFilterWheel.FocusOffsets property called")
        return self._com_object.FocusOffsets

    @property
    def Names(self):
        logger.debug(f"ASCOMFilterWheel.Names property called")
        return self._com_object.Names

    @property
    def Position(self):
        logger.debug(f"ASCOMFilterWheel.Position property called")
        return self._com_object.Position

    @Position.setter
    def Position(self, value):
        logger.debug(f"ASCOMFilterWheel.Position property set to {value}")
        self._com_object.Position = value
