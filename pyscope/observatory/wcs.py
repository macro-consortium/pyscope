from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee

class WCS(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def Solve(self, *args, **kwargs):
        pass