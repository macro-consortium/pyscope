from abc import ABC, abstractmethod

from . import DocstringInheritee

class Autofocus(ABC, metaclass=DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def Run(self, *args, **kwargs):
        pass

    @abstractmethod
    def Abort(self, *args, **kwargs):
        pass