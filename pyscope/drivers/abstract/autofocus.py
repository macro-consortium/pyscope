from abc import ABC, abstractmethod

from . import DocstringInheritee

class Autofocus(ABC, metaclass=DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass