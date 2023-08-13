import logging
from .focuser import Focuser

logger = logging.getLogger(__name__)

class ASCOMFocuser(Focuser):
    def Choose(self, FocuserID):
        logger.debug(f"ASCOMFocuser.Choose({FocuserID}) called")
        self._com_object.Choose(FocuserID)
    
    def Halt(self):
        logger.debug(f"ASCOMFocuser.Halt() called")
        self._com_object.Halt()
    
    def Move(self, Position):
        logger.debug(f"ASCOMFocuser.Move({Position}) called")
        self._com_object.Move(Position)
    
    @property
    def Absolute(self):
        logger.debug(f"ASCOMFocuser.Absolute property called")
        return self._com_object.Absolute
    
    @property
    def IsMoving(self):
        logger.debug(f"ASCOMFocuser.IsMoving property called")
        return self._com_object.IsMoving
    
    @property
    def Link(self):
        logger.debug(f"ASCOMFocuser.Link property called")
        return self._com_object.Link
    @Link.setter
    def Link(self, value):
        logger.debug(f"ASCOMFocuser.Link property set to {value}")
        self._com_object.Link = value
    
    @property
    def MaxIncrement(self):
        logger.debug(f"ASCOMFocuser.MaxIncrement property called")
        return self._com_object.MaxIncrement
    
    @property
    def MaxStep(self):
        logger.debug(f"ASCOMFocuser.MaxStep property called")
        return self._com_object.MaxStep
    
    @property
    def Position(self):
        logger.debug(f"ASCOMFocuser.Position property called")
        return self._com_object.Position
    
    @property
    def StepSize(self):
        logger.debug(f"ASCOMFocuser.StepSize property called")
        return self._com_object.StepSize
    
    @property
    def TempComp(self):
        logger.debug(f"ASCOMFocuser.TempComp property called")
        return self._com_object.TempComp
    @TempComp.setter
    def TempComp(self, value):
        logger.debug(f"ASCOMFocuser.TempComp property set to {value}")
        self._com_object.TempComp = value
    
    @property
    def TempCompAvailable(self):
        logger.debug(f"ASCOMFocuser.TempCompAvailable property called")
        return self._com_object.TempCompAvailable
    
    @property
    def Temperature(self):
        logger.debug(f"ASCOMFocuser.Temperature property called")
        return self._com_object.Temperature