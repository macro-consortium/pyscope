from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class SafetyMonitor(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def IsSafe(self):
        pass
