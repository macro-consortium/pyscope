import logging

from .ascom_device import ASCOMDevice
from .dome import Dome

logger = logging.getLogger(__name__)


class ASCOMDome(ASCOMDevice, Dome):
    def __init__(self, identifier, alpaca=False, device_number=0, protocol="http"):
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    def AbortSlew(self):
        logger.debug(f"ASCOMDome.AbortSlew() called")
        self._com_object.AbortSlew()

    def Choose(self, DomeID):
        logger.debug(f"ASCOMDome.Choose({DomeID}) called")
        self._com_object.Choose(DomeID)

    def CloseShutter(self):
        logger.debug(f"ASCOMDome.CloseShutter() called")
        self._com_object.CloseShutter()

    def FindHome(self):
        logger.debug(f"ASCOMDome.FindHome() called")
        self._com_object.FindHome()

    def OpenShutter(self):
        logger.debug(f"ASCOMDome.OpenShutter() called")
        self._com_object.OpenShutter()

    def Park(self):
        logger.debug(f"ASCOMDome.Park() called")
        self._com_object.Park()

    def SetPark(self):
        logger.debug(f"ASCOMDome.SetPark() called")
        self._com_object.SetPark()

    def SlewToAltitude(self, Altitude):
        logger.debug(f"ASCOMDome.SlewToAltitude({Altitude}) called")
        self._com_object.SlewToAltitude(Altitude)

    def SlewToAzimuth(self, Azimuth):
        logger.debug(f"ASCOMDome.SlewToAzimuth({Azimuth}) called")
        self._com_object.SlewToAzimuth(Azimuth)

    def SyncToAzimuth(self, Azimuth):
        logger.debug(f"ASCOMDome.SyncToAzimuth({Azimuth}) called")
        self._com_object.SyncToAzimuth(Azimuth)

    @property
    def Altitude(self):
        logger.debug(f"ASCOMDome.Altitude property called")
        return self._com_object.Altitude

    @property
    def AtHome(self):
        logger.debug(f"ASCOMDome.AtHome property called")
        return self._com_object.AtHome

    @property
    def AtPark(self):
        logger.debug(f"ASCOMDome.AtPark property called")
        return self._com_object.AtPark

    @property
    def Azimuth(self):
        logger.debug(f"ASCOMDome.Azimuth property called")
        return self._com_object.Azimuth

    @property
    def CanFindHome(self):
        logger.debug(f"ASCOMDome.CanFindHome property called")
        return self._com_object.CanFindHome

    @property
    def CanPark(self):
        logger.debug(f"ASCOMDome.CanPark property called")
        return self._com_object.CanPark

    @property
    def CanSetAltitude(self):
        logger.debug(f"ASCOMDome.CanSetAltitude property called")
        return self._com_object.CanSetAltitude

    @property
    def CanSetAzimuth(self):
        logger.debug(f"ASCOMDome.CanSetAzimuth property called")
        return self._com_object.CanSetAzimuth

    @property
    def CanSetPark(self):
        logger.debug(f"ASCOMDome.CanSetPark property called")
        return self._com_object.CanSetPark

    @property
    def CanSetShutter(self):
        logger.debug(f"ASCOMDome.CanSetShutter property called")
        return self._com_object.CanSetShutter

    @property
    def CanSlave(self):
        logger.debug(f"ASCOMDome.CanSlave property called")
        return self._com_object.CanSlave

    @property
    def CanSyncAzimuth(self):
        logger.debug(f"ASCOMDome.CanSyncAzimuth property called")
        return self._com_object.CanSyncAzimuth

    @property
    def ShutterStatus(self):
        logger.debug(f"ASCOMDome.ShutterStatus property called")
        return self._com_object.ShutterStatus

    @property
    def Slaved(self):
        logger.debug(f"ASCOMDome.Slaved property called")
        return self._com_object.Slaved

    @property
    def Slewing(self):
        logger.debug(f"ASCOMDome.Slewing property called")
        return self._com_object.Slewing
