from abc import ABC, abstractmethod

from . import DocstringInheritee

class FilterWheel(ABC, metaclass=DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def FocusOffsets(self):
        pass

    @property
    @abstractmethod
    def Names(self):
        pass

    @property
    @abstractmethod
    def Position(self):
        pass
    @Position.setter
    @abstractmethod
    def Position(self, value):
        pass