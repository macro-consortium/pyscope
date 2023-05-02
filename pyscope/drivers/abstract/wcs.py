from abc import ABC, abstractmethod

class WCS(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def Solve(self, *args, **kwargs):
        pass