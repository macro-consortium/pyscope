from . import Driver
from .. import abstract

class Dome(Driver, abstract.Dome):
    def AbortSlew(self):
        self._com_object.AbortSlew()

    def Choose(self, DomeID):
        self._com_object.Choose(DomeID)

    def CloseShutter(self):
        self._com_object.CloseShutter()
    
    def FindHome(self):
        self._com_object.FindHome()
    
    def OpenShutter(self):
        self._com_object.OpenShutter()
    
    def Park(self):
        self._com_object.Park()
    
    def SetPark(self):
        self._com_object.SetPark()
    
    def SlewToAltitude(self, Altitude):
        self._com_object.SlewToAltitude(Altitude)
    
    def SlewToAzimuth(self, Azimuth):
        self._com_object.SlewToAzimuth(Azimuth)
    
    def SyncToAzimuth(self, Azimuth):
        self._com_object.SyncToAzimuth(Azimuth)
    
    @property
    def Altitude(self):
        return self._com_object.Altitude
    
    @property
    def AtHome(self):
        return self._com_object.AtHome
    
    @property
    def AtPark(self):
        return self._com_object.AtPark
    
    @property
    def Azimuth(self):
        return self._com_object.Azimuth
    
    @property
    def CanFindHome(self):
        return self._com_object.CanFindHome
    
    @property
    def CanPark(self):
        return self._com_object.CanPark

    @property
    def CanSetAltitude(self):
        return self._com_object.CanSetAltitude

    @property
    def CanSetAzimuth(self):
        return self._com_object.CanSetAzimuth

    @property
    def CanSetPark(self):
        return self._com_object.CanSetPark

    @property
    def CanSetShutter(self):
        return self._com_object.CanSetShutter

    @property
    def CanSlave(self):
        return self._com_object.CanSlave

    @property
    def CanSyncAzimuth(self):
        return self._com_object.CanSyncAzimuth

    @property
    def ShutterStatus(self):
        return self._com_object.ShutterStatus

    @property
    def Slaved(self):
        return self._com_object.Slaved

    @property
    def Slewing(self):
        return self._com_object.Slewing