from abc import ABC, abstractmethod

from . import DocstringInheritee

class Dome(ABC, metaclass=DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def AbortSlew(self):
        pass

    @abstractmethod
    def CloseShutter(self):
        pass
    
    @abstractmethod
    def FindHome(self):
        pass
    
    @abstractmethod
    def OpenShutter(self):
        pass
    
    @abstractmethod
    def Park(self):
        pass
    
    @abstractmethod
    def SetPark(self):
        pass
    
    @abstractmethod
    def SlewToAltitude(self, Altitude):
        pass
    
    @abstractmethod
    def SlewToAzimuth(self, Azimuth):
        pass
    
    @abstractmethod
    def SyncToAzimuth(self, Azimuth):
        pass
    
    @property
    @abstractmethod
    def Altitude(self):
        pass
    
    @property
    @abstractmethod
    def AtHome(self):
        pass
    
    @property
    @abstractmethod
    def AtPark(self):
        pass
    
    @property
    @abstractmethod
    def Azimuth(self):
        pass
    
    @property
    @abstractmethod
    def CanFindHome(self):
        pass
    
    @property
    @abstractmethod
    def CanPark(self):
        pass

    @property
    @abstractmethod
    def CanSetAltitude(self):
        pass

    @property
    @abstractmethod
    def CanSetAzimuth(self):
        pass

    @property
    @abstractmethod
    def CanSetPark(self):
        pass

    @property
    @abstractmethod
    def CanSetShutter(self):
        pass

    @property
    @abstractmethod
    def CanSlave(self):
        pass

    @property
    @abstractmethod
    def CanSyncAzimuth(self):
        pass

    @property
    @abstractmethod
    def ShutterStatus(self):
        pass

    @property
    @abstractmethod
    def Slaved(self):
        pass

    @property
    @abstractmethod
    def Slewing(self):
        pass