import logging

from .ascom_device import ASCOMDevice
from .rotator import Rotator

logger = logging.getLogger(__name__)


class ASCOMRotator(ASCOMDevice, Rotator):
    def __init__(self, identifier, alpaca=False, device_number=0, protocol="http"):
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    def Halt(self):
        logger.debug("ASCOMRotator.Halt() called")
        self._device.Halt()

    def Move(self, Position):
        logger.debug(f"ASCOMRotator.Move({Position}) called")
        self._device.Move(Position)

    def MoveAbsolute(self, Position):
        logger.debug(f"ASCOMRotator.MoveAbsolute({Position}) called")
        self._device.MoveAbsolute(Position)

    def MoveMechanical(self, Position):
        logger.debug(f"ASCOMRotator.MoveMechanical({Position}) called")
        self._device.MoveMechanical(Position)

    def Sync(self, Position):
        logger.debug(f"ASCOMRotator.Sync({Position}) called")
        self._device.Sync(Position)

    @property
    def CanReverse(self):
        logger.debug("ASCOMRotator.CanReverse property called")
        return self._device.CanReverse

    @property
    def IsMoving(self):
        logger.debug("ASCOMRotator.IsMoving property called")
        return self._device.IsMoving

    @property
    def MechanicalPosition(self):
        logger.debug("ASCOMRotator.MechanicalPosition property called")
        return self._device.MechanicalPosition

    @property
    def Position(self):
        logger.debug("ASCOMRotator.Position property called")
        return self._device.Position

    @property
    def Reverse(self):
        logger.debug("ASCOMRotator.Reverse property called")
        return self._device.Reverse

    @Reverse.setter
    def Reverse(self, value):
        logger.debug(f"ASCOMRotator.Reverse property set to {value}")
        self._device.Reverse = value

    @property
    def StepSize(self):
        logger.debug("ASCOMRotator.StepSize property called")
        return self._device.StepSize

    @property
    def TargetPosition(self):
        logger.debug("ASCOMRotator.TargetPosition property called")
        return self._device.TargetPosition
