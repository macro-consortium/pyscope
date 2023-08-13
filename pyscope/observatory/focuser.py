from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee

class Focuser(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def Halt(self):
        pass

    @abstractmethod
    def Move(self, Position):
        pass

    @property
    @abstractmethod
    def Absolute(self):
        pass
    @Absolute.setter
    @abstractmethod
    def Absolute(self, value):
        pass

    @property
    @abstractmethod
    def IsMoving(self):
        pass

    @property
    @abstractmethod
    def Link(self):
        pass
    @Link.setter
    @abstractmethod
    def Link(self, value):
        pass

    @property
    @abstractmethod
    def MaxIncrement(self):
        pass

    @property
    @abstractmethod
    def MaxStep(self):
        pass

    @property
    @abstractmethod
    def Position(self):
        pass

    @property
    @abstractmethod
    def StepSize(self):
        pass

    @property
    @abstractmethod
    def TempComp(self):
        pass
    @TempComp.setter
    @abstractmethod
    def TempComp(self, value):
        pass

    @property
    @abstractmethod
    def TempCompAvailable(self):
        pass

    @property
    @abstractmethod
    def Temperature(self):
        pass
    @Temperature.setter
    @abstractmethod
    def Temperature(self, value):
        pass