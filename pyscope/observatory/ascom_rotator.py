from .rotator import Rotator

class ASCOMRotator(Rotator):
    def Choose(self, RotatorID):
        self._com_object.Choose(RotatorID)
    
    def Halt(self):
        self._com_object.Halt()
    
    def Move(self, Position):
        self._com_object.Move(Position)
    
    def MoveAbsolute(self, Position):
        self._com_object.MoveAbsolute(Position)
    
    def MoveMechanical(self, Position):
        self._com_object.MoveMechanical(Position)
    
    def Sync(self, Position):
        self._com_object.Sync(Position)
    
    @property
    def CanReverse(self):
        return self._com_object.CanReverse
    
    @property
    def IsMoving(self):
        return self._com_object.IsMoving
    
    @property
    def MechanicalPosition(self):
        return self._com_object.MechanicalPosition
    
    @property
    def Position(self):
        return self._com_object.Position

    @property
    def Reverse(self):
        return self._com_object.Reverse
    @Reverse.setter
    def Reverse(self, value):
        self._com_object.Reverse = value

    @property
    def StepSize(self):
        return self._com_object.StepSize
    
    @property
    def TargetPosition(self):
        return self._com_object.TargetPosition