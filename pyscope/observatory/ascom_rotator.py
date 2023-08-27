import logging

from .ascom_driver import ASCOMDriver
from .rotator import Rotator

logger = logging.getLogger(__name__)


class ASCOMRotator(Rotator, ASCOMDriver):
    def Choose(self, RotatorID):
        logger.debug(f"ASCOMRotator.Choose({RotatorID}) called")
        self._com_object.Choose(RotatorID)

    def Halt(self):
        logger.debug("ASCOMRotator.Halt() called")
        self._com_object.Halt()

    def Move(self, Position):
        logger.debug(f"ASCOMRotator.Move({Position}) called")
        self._com_object.Move(Position)

    def MoveAbsolute(self, Position):
        logger.debug(f"ASCOMRotator.MoveAbsolute({Position}) called")
        self._com_object.MoveAbsolute(Position)

    def MoveMechanical(self, Position):
        logger.debug(f"ASCOMRotator.MoveMechanical({Position}) called")
        self._com_object.MoveMechanical(Position)

    def Sync(self, Position):
        logger.debug(f"ASCOMRotator.Sync({Position}) called")
        self._com_object.Sync(Position)

    @property
    def CanReverse(self):
        logger.debug("ASCOMRotator.CanReverse property called")
        return self._com_object.CanReverse

    @property
    def IsMoving(self):
        logger.debug("ASCOMRotator.IsMoving property called")
        return self._com_object.IsMoving

    @property
    def MechanicalPosition(self):
        logger.debug("ASCOMRotator.MechanicalPosition property called")
        return self._com_object.MechanicalPosition

    @property
    def Position(self):
        logger.debug("ASCOMRotator.Position property called")
        return self._com_object.Position

    @property
    def Reverse(self):
        logger.debug("ASCOMRotator.Reverse property called")
        return self._com_object.Reverse

    @Reverse.setter
    def Reverse(self, value):
        logger.debug(f"ASCOMRotator.Reverse property set to {value}")
        self._com_object.Reverse = value

    @property
    def StepSize(self):
        logger.debug("ASCOMRotator.StepSize property called")
        return self._com_object.StepSize

    @property
    def TargetPosition(self):
        logger.debug("ASCOMRotator.TargetPosition property called")
        return self._com_object.TargetPosition
