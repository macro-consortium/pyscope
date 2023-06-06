from abc import ABC, abstractmethod

from abstract import DocstringInheritee

class CoverCalibrator(ABC, metaclass=DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def CalibratorOff(self):
        pass

    @abstractmethod
    def CalibratorOn(self, Brightness):
        pass

    @abstractmethod
    def CloseCover(self):
        pass

    @abstractmethod
    def HaltCover(self):
        pass

    @abstractmethod
    def OpenCover(self):
        pass

    @property
    @abstractmethod
    def Brightness(self):
        pass

    @property
    @abstractmethod
    def CalibratorState(self):
        pass

    @property
    @abstractmethod
    def CoverState(self):
        pass

    @property
    @abstractmethod
    def MaxBrightness(self):
        pass