from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class Switch(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def CanWrite(self, ID):
        pass

    @abstractmethod
    def GetSwitch(self, ID):
        pass

    @abstractmethod
    def GetSwitchDescription(self, ID):
        pass

    @abstractmethod
    def GetSwitchName(self, ID):
        pass

    @abstractmethod
    def MaxSwitchValue(self, ID):
        pass

    @abstractmethod
    def MinSwitchValue(self, ID):
        pass

    @abstractmethod
    def SetSwitch(self, ID, State):
        pass

    @abstractmethod
    def SetSwitchName(self, ID, Name):
        pass

    @abstractmethod
    def SetSwitchValue(self, ID, Value):
        pass

    @abstractmethod
    def SwitchStep(self, ID):
        pass

    @abstractmethod
    def RebootSwitch(self, ID):
        pass

    @abstractmethod
    def ToggleSwitch(self, ID):
        pass

    @abstractmethod
    def AllOn(self):
        pass

    @abstractmethod
    def AllOff(self):
        pass

    @abstractmethod
    def PowerCycleAll(self):
        pass

    @abstractmethod
    def Status(self):
        pass

    @property
    @abstractmethod
    def MaxSwitch(self):
        pass
