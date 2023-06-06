from abc import ABC, abstractmethod

from . import DocstringInheritee

class WCS(ABC, metaclass=DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def Solve(self, *args, **kwargs):
        pass