from abc import ABC, abstractmethod

class Driver(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def Connected(self):
        pass
    @Connected.setter
    @abstractmethod
    def Connected(self, value):
        pass

    @property
    @abstractmethod
    def Name(self):
        pass