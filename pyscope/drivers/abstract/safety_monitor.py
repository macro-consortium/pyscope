from abc import ABC, abstractmethod

class SafetyMonitor(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def IsSafe(self):
        pass