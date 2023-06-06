from abc import ABC, abstractmethod

from . import DocstringInheritee

class Driver(ABC, metaclass=DocstringInheritee):
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