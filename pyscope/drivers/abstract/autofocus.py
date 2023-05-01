from abc import ABC, abstractmethod

class Autofocus(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass