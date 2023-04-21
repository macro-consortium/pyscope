from abc import ABC, abstractmethod

class Camera(ABC):
    @abstractmethod
    def StartExposure(self, duration, shutter):
        pass

    @abstractmethod
    def AbortExposure(self):
        pass

class CoverCalibrator(ABC):
    pass

class Dome(ABC):
    pass

class FilterWheel(ABC):
    pass

class Focuser(ABC):
    pass

class ObservingConditions(ABC):
    pass

'''class Rotator(ABC):
    pass'''

'''class SafetyMonitor(ABC):
    pass'''

'''class Switch(ABC):
    pass'''

class Telescope(ABC):
    pass

'''class Video(ABC):
    pass'''