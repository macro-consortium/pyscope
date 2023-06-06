from abc import ABC, abstractmethod

from abstract import DocstringInheritee

class Rotator(ABC, metaclass=DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def Halt(self):
        pass

    @abstractmethod
    def Move(self, Position):
        pass

    @abstractmethod
    def MoveAbsolute(self, Position):
        pass

    @abstractmethod
    def MoveMechanical(self, Position):
        pass

    @abstractmethod
    def Sync(self, Position):
        pass

    @property
    @abstractmethod
    def CanReverse(self):
        pass

    @property
    @abstractmethod
    def IsMoving(self):
        pass

    @property
    @abstractmethod
    def MechanicalPosition(self):
        pass

    @property
    @abstractmethod
    def Position(self):
        pass

    @property
    @abstractmethod
    def Reverse(self):
        pass
    @Reverse.setter
    @abstractmethod
    def Reverse(self, value):
        pass

    @property
    @abstractmethod
    def StepSize(self):
        pass

    @property
    @abstractmethod
    def TargetPosition(self):
        pass