import logging

from .ascom_driver import ASCOMDriver
from .telescope import Telescope

logger = logging.getLogger(__name__)


class ASCOMTelescope(Telescope, ASCOMDriver):
    def AbortSlew(self):
        logger.debug("ASCOMTelescope.AbortSlew() called")
        self._com_object.AbortSlew()

    def AxisRates(self, Axis):
        logger.debug(f"ASCOMTelescope.AxisRates({Axis}) called")
        return self._com_object.AxisRates(Axis)

    def CanMoveAxis(self, Axis):
        logger.debug(f"ASCOMTelescope.CanMoveAxis({Axis}) called")
        return self._com_object.CanMoveAxis(Axis)

    def Choose(self, TelescopeID):
        logger.debug(f"ASCOMTelescope.Choose({TelescopeID}) called")
        self._com_object.Choose(TelescopeID)

    def DestinationSideOfPier(self, RightAscension, Declination):
        logger.debug(
            f"ASCOMTelescope.DestinationSideOfPier({RightAscension}, {Declination}) called"
        )
        return self._com_object.DestinationSideOfPier(RightAscension, Declination)

    def FindHome(self):
        logger.debug("ASCOMTelescope.FindHome() called")
        self._com_object.FindHome()

    def MoveAxis(self, Axis, Rate):
        logger.debug(f"ASCOMTelescope.MoveAxis({Axis}, {Rate}) called")
        self._com_object.MoveAxis(Axis, Rate)

    def Park(self):
        logger.debug("ASCOMTelescope.Park() called")
        self._com_object.Park()

    def PulseGuide(self, Direction, Duration):
        logger.debug(f"ASCOMTelescope.PulseGuide({Direction}, {Duration}) called")
        self._com_object.PulseGuide(Direction, Duration)

    def SetPark(self):
        logger.debug("ASCOMTelescope.SetPark() called")
        self._com_object.SetPark()

    def SlewToAltAz(self, Azimuth, Altitude):
        logger.debug(f"ASCOMTelescope.SlewToAltAz({Azimuth}, {Altitude}) called")
        self._com_object.SlewToAltAz(Azimuth, Altitude)

    def SlewToAltAzAsync(self, Azimuth, Altitude):
        logger.debug(f"ASCOMTelescope.SlewToAltAzAsync({Azimuth}, {Altitude}) called")
        self._com_object.SlewToAltAzAsync(Azimuth, Altitude)

    def SlewToCoordinates(self, RightAscension, Declination):
        logger.debug(
            f"ASCOMTelescope.SlewToCoordinates({RightAscension}, {Declination}) called"
        )
        self._com_object.SlewToCoordinates(RightAscension, Declination)

    def SlewToCoordinatesAsync(self, RightAscension, Declination):
        logger.debug(
            f"ASCOMTelescope.SlewToCoordinatesAsync({RightAscension}, {Declination}) called"
        )
        self._com_object.SlewToCoordinatesAsync(RightAscension, Declination)

    def SlewToTarget(self):
        logger.debug("ASCOMTelescope.SlewToTarget() called")
        self._com_object.SlewToTarget()

    def SlewToTargetAsync(self):
        logger.debug("ASCOMTelescope.SlewToTargetAsync() called")
        self._com_object.SlewToTargetAsync()

    def SyncToAltAz(self, Azimuth, Altitude):
        logger.debug(f"ASCOMTelescope.SyncToAltAz({Azimuth}, {Altitude}) called")
        self._com_object.SyncToAltAz(Azimuth, Altitude)

    def SyncToCoordinates(self, RightAscension, Declination):
        logger.debug(
            f"ASCOMTelescope.SyncToCoordinates({RightAscension}, {Declination}) called"
        )
        self._com_object.SyncToCoordinates(RightAscension, Declination)

    def SyncToTarget(self):
        logger.debug("ASCOMTelescope.SyncToTarget() called")
        self._com_object.SyncToTarget()

    def Unpark(self):
        logger.debug("ASCOMTelescope.Unpark() called")
        self._com_object.Unpark()

    @property
    def AlignmentMode(self):
        logger.debug("ASCOMTelescope.AlignmentMode property accessed")
        return self._com_object.AlignmentMode

    @property
    def Altitude(self):
        logger.debug("ASCOMTelescope.Altitude property accessed")
        return self._com_object.Altitude

    @property
    def ApertureArea(self):
        logger.debug("ASCOMTelescope.ApertureArea property accessed")
        return self._com_object.ApertureArea

    @property
    def ApertureDiameter(self):
        logger.debug("ASCOMTelescope.ApertureDiameter property accessed")
        return self._com_object.ApertureDiameter

    @property
    def AtHome(self):
        logger.debug("ASCOMTelescope.AtHome property accessed")
        return self._com_object.AtHome

    @property
    def AtPark(self):
        logger.debug("ASCOMTelescope.AtPark property accessed")
        return self._com_object.AtPark

    @property
    def Azimuth(self):
        logger.debug("ASCOMTelescope.Azimuth property accessed")
        return self._com_object.Azimuth

    @property
    def CanFindHome(self):
        logger.debug("ASCOMTelescope.CanFindHome property accessed")
        return self._com_object.CanFindHome

    @property
    def CanPark(self):
        logger.debug("ASCOMTelescope.CanPark property accessed")
        return self._com_object.CanPark

    def CanPulseGuide(self, Direction):
        logger.debug(f"ASCOMTelescope.CanPulseGuide({Direction}) called")
        return self._com_object.CanPulseGuide(Direction)

    @property
    def CanSetDeclinationRate(self):
        logger.debug("ASCOMTelescope.CanSetDeclinationRate property accessed")
        return self._com_object.CanSetDeclinationRate

    @property
    def CanSetGuideRates(self):
        logger.debug("ASCOMTelescope.CanSetGuideRates property accessed")
        return self._com_object.CanSetGuideRates

    @property
    def CanSetPark(self):
        logger.debug("ASCOMTelescope.CanSetPark property accessed")
        return self._com_object.CanSetPark

    @property
    def CanSetPierSide(self):
        logger.debug("ASCOMTelescope.CanSetPierSide property accessed")
        return self._com_object.CanSetPierSide

    @property
    def CanSetRightAscensionRate(self):
        logger.debug("ASCOMTelescope.CanSetRightAscensionRate property accessed")
        return self._com_object.CanSetRightAscensionRate

    @property
    def CanSetTracking(self):
        logger.debug("ASCOMTelescope.CanSetTracking property accessed")
        return self._com_object.CanSetTracking

    @property
    def CanSlew(self):
        logger.debug("ASCOMTelescope.CanSlew property accessed")
        return self._com_object.CanSlew

    @property
    def CanSlewAltAz(self):
        logger.debug("ASCOMTelescope.CanSlewAltAz property accessed")
        return self._com_object.CanSlewAltAz

    @property
    def CanSlewAltAzAsync(self):
        logger.debug("ASCOMTelescope.CanSlewAltAzAsync property accessed")
        return self._com_object.CanSlewAltAzAsync

    @property
    def CanSlewAsync(self):
        logger.debug("ASCOMTelescope.CanSlewAsync property accessed")
        return self._com_object.CanSlewAsync

    @property
    def CanSync(self):
        logger.debug("ASCOMTelescope.CanSync property accessed")
        return self._com_object.CanSync

    @property
    def CanSyncAltAz(self):
        logger.debug("ASCOMTelescope.CanSyncAltAz property accessed")
        return self._com_object.CanSyncAltAz

    @property
    def CanUnpark(self):
        logger.debug("ASCOMTelescope.CanUnpark property accessed")
        return self._com_object.CanUnpark

    @property
    def Declination(self):
        logger.debug("ASCOMTelescope.Declination property accessed")
        return self._com_object.Declination

    @property
    def DeclinationRate(self):
        logger.debug("ASCOMTelescope.DeclinationRate property accessed")
        return self._com_object.DeclinationRate

    @DeclinationRate.setter
    def DeclinationRate(self, value):
        logger.debug(f"ASCOMTelescope.DeclinationRate set to {value}")
        self._com_object.DeclinationRate = value

    @property
    def DoesRefraction(self):
        logger.debug("ASCOMTelescope.DoesRefraction property accessed")
        return self._com_object.DoesRefraction

    @DoesRefraction.setter
    def DoesRefraction(self, value):
        logger.debug(f"ASCOMTelescope.DoesRefraction set to {value}")
        self._com_object.DoesRefraction = value

    @property
    def EquatorialSystem(self):
        logger.debug("ASCOMTelescope.EquatorialSystem property accessed")
        return self._com_object.EquatorialSystem

    @property
    def FocalLength(self):
        logger.debug("ASCOMTelescope.FocalLength property accessed")
        return self._com_object.FocalLength

    @property
    def GuideRateDeclination(self):
        logger.debug("ASCOMTelescope.GuideRateDeclination property accessed")
        return self._com_object.GuideRateDeclination

    @GuideRateDeclination.setter
    def GuideRateDeclination(self, value):
        logger.debug(f"ASCOMTelescope.GuideRateDeclination set to {value}")
        self._com_object.GuideRateDeclination = value

    @property
    def GuideRateRightAscension(self):
        logger.debug("ASCOMTelescope.GuideRateRightAscension property accessed")
        return self._com_object.GuideRateRightAscension

    @GuideRateRightAscension.setter
    def GuideRateRightAscension(self, value):
        logger.debug(f"ASCOMTelescope.GuideRateRightAscension set to {value}")
        self._com_object.GuideRateRightAscension = value

    @property
    def IsPulseGuiding(self):
        logger.debug("ASCOMTelescope.IsPulseGuiding property accessed")
        return self._com_object.IsPulseGuiding

    @property
    def RightAscension(self):
        logger.debug("ASCOMTelescope.RightAscension property accessed")
        return self._com_object.RightAscension

    @property
    def RightAscensionRate(self):
        logger.debug("ASCOMTelescope.RightAscensionRate property accessed")
        return self._com_object.RightAscensionRate

    @RightAscensionRate.setter
    def RightAscensionRate(self, value):
        logger.debug(f"ASCOMTelescope.RightAscensionRate set to {value}")
        self._com_object.RightAscensionRate = value

    @property
    def SideOfPier(self):
        logger.debug("ASCOMTelescope.SideOfPier property accessed")
        return self._com_object.SideOfPier

    @SideOfPier.setter
    def SideOfPier(self, value):
        logger.debug(f"ASCOMTelescope.SideOfPier set to {value}")
        self._com_object.SideOfPier = value

    @property
    def SiderealTime(self):
        logger.debug("ASCOMTelescope.SiderealTime property accessed")
        return self._com_object.SiderealTime

    @property
    def SiteElevation(self):
        logger.debug("ASCOMTelescope.SiteElevation property accessed")
        return self._com_object.SiteElevation

    @SiteElevation.setter
    def SiteElevation(self, value):
        logger.debug(f"ASCOMTelescope.SiteElevation set to {value}")
        self._com_object.SiteElevation = value

    @property
    def SiteLatitude(self):
        logger.debug("ASCOMTelescope.SiteLatitude property accessed")
        return self._com_object.SiteLatitude

    @SiteLatitude.setter
    def SiteLatitude(self, value):
        logger.debug(f"ASCOMTelescope.SiteLatitude set to {value}")
        self._com_object.SiteLatitude = value

    @property
    def SiteLongitude(self):
        logger.debug("ASCOMTelescope.SiteLongitude property accessed")
        return self._com_object.SiteLongitude

    @SiteLongitude.setter
    def SiteLongitude(self, value):
        logger.debug(f"ASCOMTelescope.SiteLongitude set to {value}")
        self._com_object.SiteLongitude = value

    @property
    def Slewing(self):
        logger.debug("ASCOMTelescope.Slewing property accessed")
        return self._com_object.Slewing

    @property
    def SlewSettleTime(self):
        logger.debug("ASCOMTelescope.SlewSettleTime property accessed")
        return self._com_object.SlewSettleTime

    @SlewSettleTime.setter
    def SlewSettleTime(self, value):
        logger.debug(f"ASCOMTelescope.SlewSettleTime set to {value}")
        self._com_object.SlewSettleTime = value

    @property
    def TargetDeclination(self):
        logger.debug("ASCOMTelescope.TargetDeclination property accessed")
        return self._com_object.TargetDeclination

    @TargetDeclination.setter
    def TargetDeclination(self, value):
        logger.debug(f"ASCOMTelescope.TargetDeclination set to {value}")
        self._com_object.TargetDeclination = value

    @property
    def TargetRightAscension(self):
        logger.debug("ASCOMTelescope.TargetRightAscension property accessed")
        return self._com_object.TargetRightAscension

    @TargetRightAscension.setter
    def TargetRightAscension(self, value):
        logger.debug(f"ASCOMTelescope.TargetRightAscension set to {value}")
        self._com_object.TargetRightAscension = value

    @property
    def Tracking(self):
        logger.debug("ASCOMTelescope.Tracking property accessed")
        return self._com_object.Tracking

    @Tracking.setter
    def Tracking(self, value):
        logger.debug(f"ASCOMTelescope.Tracking set to {value}")
        self._com_object.Tracking = value

    @property
    def TrackingRate(self):
        logger.debug("ASCOMTelescope.TrackingRate property accessed")
        return self._com_object.TrackingRate

    @TrackingRate.setter
    def TrackingRate(self, value):
        logger.debug(f"ASCOMTelescope.TrackingRate set to {value}")
        self._com_object.TrackingRate = value

    @property
    def TrackingRates(self):
        logger.debug("ASCOMTelescope.TrackingRates property accessed")
        return self._com_object.TrackingRates

    @property
    def UTCDate(self):
        logger.debug("ASCOMTelescope.UTCDate property accessed")
        return self._com_object.UTCDate

    @UTCDate.setter
    def UTCDate(self, value):
        logger.debug(f"ASCOMTelescope.UTCDate set to {value}")
        self._com_object.UTCDate = value
