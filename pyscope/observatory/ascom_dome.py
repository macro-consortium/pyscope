import logging

from .ascom_device import ASCOMDevice
from .dome import Dome

logger = logging.getLogger(__name__)


class ASCOMDome(ASCOMDevice, Dome):
    def __init__(
        self, identifier, alpaca=False, device_number=0, protocol="http"
    ):
        """
        ASCOM implementation of the Dome abstract base class.

        This class provides the functionality to control an ASCOM-compatible dome device,
        including methods for controlling the dome's movement and shutter.

        Parameters
        ----------
        identifier : `str`
            The unique device identifier. This can be the ProgID for COM devices or the device number for Alpaca devices.
        alpaca : `bool`, default : `False`, optional
            Whether to use the Alpaca protocol. If `False`, the COM protocol is used.
        device_number : `int`, default : 0, optional
            The device number for Alpaca devices.
        protocol : `str`, default : "http", optional
            The protocol to use for Alpaca devices.
        """
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    def AbortSlew(self):
        logger.debug(f"ASCOMDome.AbortSlew() called")
        self._device.AbortSlew()

    def CloseShutter(self):
        logger.debug(f"ASCOMDome.CloseShutter() called")
        self._device.CloseShutter()

    def FindHome(self):
        logger.debug(f"ASCOMDome.FindHome() called")
        self._device.FindHome()

    def OpenShutter(self):
        logger.debug(f"ASCOMDome.OpenShutter() called")
        self._device.OpenShutter()

    def Park(self):
        logger.debug(f"ASCOMDome.Park() called")
        self._device.Park()

    def SetPark(self):
        logger.debug(f"ASCOMDome.SetPark() called")
        self._device.SetPark()

    def SlewToAltitude(self, Altitude):
        logger.debug(f"ASCOMDome.SlewToAltitude({Altitude}) called")
        self._device.SlewToAltitude(Altitude)

    def SlewToAzimuth(self, Azimuth):
        logger.debug(f"ASCOMDome.SlewToAzimuth({Azimuth}) called")
        self._device.SlewToAzimuth(Azimuth)

    def SyncToAzimuth(self, Azimuth):
        logger.debug(f"ASCOMDome.SyncToAzimuth({Azimuth}) called")
        self._device.SyncToAzimuth(Azimuth)

    @property
    def Altitude(self):
        logger.debug(f"ASCOMDome.Altitude property called")
        return self._device.Altitude

    @property
    def AtHome(self):
        logger.debug(f"ASCOMDome.AtHome property called")
        return self._device.AtHome

    @property
    def AtPark(self):
        logger.debug(f"ASCOMDome.AtPark property called")
        return self._device.AtPark

    @property
    def Azimuth(self):
        logger.debug(f"ASCOMDome.Azimuth property called")
        return self._device.Azimuth

    @property
    def CanFindHome(self):
        logger.debug(f"ASCOMDome.CanFindHome property called")
        return self._device.CanFindHome

    @property
    def CanPark(self):
        logger.debug(f"ASCOMDome.CanPark property called")
        return self._device.CanPark

    @property
    def CanSetAltitude(self):
        logger.debug(f"ASCOMDome.CanSetAltitude property called")
        return self._device.CanSetAltitude

    @property
    def CanSetAzimuth(self):
        logger.debug(f"ASCOMDome.CanSetAzimuth property called")
        return self._device.CanSetAzimuth

    @property
    def CanSetPark(self):
        logger.debug(f"ASCOMDome.CanSetPark property called")
        return self._device.CanSetPark

    @property
    def CanSetShutter(self):
        logger.debug(f"ASCOMDome.CanSetShutter property called")
        return self._device.CanSetShutter

    @property
    def CanSlave(self):
        logger.debug(f"ASCOMDome.CanSlave property called")
        return self._device.CanSlave

    @property
    def CanSyncAzimuth(self):
        logger.debug(f"ASCOMDome.CanSyncAzimuth property called")
        return self._device.CanSyncAzimuth

    @property
    def ShutterStatus(self):
        """
        The status of the dome shutter or roof structure. (`ShutterState <https://ascom-standards.org/Help/Developer/html/T_ASCOM_DeviceInterface_ShutterState.htm>`_)

        Raises error if there's no shutter control, or if the shutter status can not be read, returns the last shutter state.
        Enum values and their representations are as follows:

            * 0 : Open
            * 1 : Closed
            * 2 : Opening
            * 3 : Closing
            * 4 : Error
            * Other : Unknown
        """
        logger.debug(f"ASCOMDome.ShutterStatus property called")
        shutter_status = self._device.ShutterStatus
        if shutter_status == 0:
            shutter_status_text = "Open"
        elif shutter_status == 1:
            shutter_status_text = "Closed"
        elif shutter_status == 2:
            shutter_status_text = "Opening"
        elif shutter_status == 3:
            shutter_status_text = "Closing"
        elif shutter_status == 4:
            shutter_status_text = "Error"
        else:
            shutter_status_text = "Unknown"
        return shutter_status_text

    @property
    def Slaved(self):
        logger.debug(f"ASCOMDome.Slaved property called")
        return self._device.Slaved

    @property
    def Slewing(self):
        logger.debug(f"ASCOMDome.Slewing property called")
        return self._device.Slewing
