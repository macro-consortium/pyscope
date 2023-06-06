from abc import ABC, abstractmethod

from abstract import DocstringInheritee

class Autofocus(ABC, metaclass=DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass