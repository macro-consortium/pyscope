from .focuser import Focuser

class ASCOMFocuser(Focuser):
    def Choose(self, FocuserID):
        self._com_object.Choose(FocuserID)
    
    def Halt(self):
        self._com_object.Halt()
    
    def Move(self, Position):
        self._com_object.Move(Position)
    
    @property
    def Absolute(self):
        return self._com_object.Absolute
    
    @property
    def IsMoving(self):
        return self._com_object.IsMoving
    
    @property
    def Link(self):
        return self._com_object.Link
    @Link.setter
    def Link(self, value):
        self._com_object.Link = value
    
    @property
    def MaxIncrement(self):
        return self._com_object.MaxIncrement
    
    @property
    def MaxStep(self):
        return self._com_object.MaxStep
    
    @property
    def Position(self):
        return self._com_object.Position
    
    @property
    def StepSize(self):
        return self._com_object.StepSize
    
    @property
    def TempComp(self):
        return self._com_object.TempComp
    @TempComp.setter
    def TempComp(self, value):
        self._com_object.TempComp = value
    
    @property
    def TempCompAvailable(self):
        return self._com_object.TempCompAvailable
    
    @property
    def Temperature(self):
        return self._com_object.Temperature