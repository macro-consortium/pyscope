from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class Autofocus(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def Run(self, *args, **kwargs):
        pass

    @abstractmethod
    def Abort(self, *args, **kwargs):
        pass
