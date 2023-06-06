from abc import ABC, abstractmethod

from abstract import DocstringInheritee

class SafetyMonitor(ABC, metaclass=DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def IsSafe(self):
        pass