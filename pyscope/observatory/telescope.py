from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class Telescope(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def AbortSlew(self):
        pass

    @abstractmethod
    def AxisRates(self, Axis):
        pass

    @abstractmethod
    def CanMoveAxis(self, Axis):
        pass

    @abstractmethod
    def DestinationSideOfPier(self, RightAscension, Declination):
        pass

    @abstractmethod
    def FindHome(self):
        pass

    @abstractmethod
    def MoveAxis(self, Axis, Rate):
        pass

    @abstractmethod
    def Park(self):
        pass

    @abstractmethod
    def PulseGuide(self, Direction, Duration):
        pass

    @abstractmethod
    def SetPark(self):
        pass

    @abstractmethod
    def SlewToAltAz(self, Azimuth, Altitude):
        pass

    @abstractmethod
    def SlewToAltAzAsync(self, Azimuth, Altitude):
        pass

    @abstractmethod
    def SlewToCoordinates(self, RightAscension, Declination):
        pass

    @abstractmethod
    def SlewToCoordinatesAsync(self, RightAscension, Declination):
        pass

    @abstractmethod
    def SlewToTarget(self):
        pass

    @abstractmethod
    def SlewToTargetAsync(self):
        pass

    @abstractmethod
    def SyncToAltAz(self, Azimuth, Altitude):
        pass

    @abstractmethod
    def SyncToCoordinates(self, RightAscension, Declination):
        pass

    @abstractmethod
    def SyncToTarget(self):
        pass

    @abstractmethod
    def Unpark(self):
        pass

    @property
    @abstractmethod
    def AlignmentMode(self):
        pass

    @AlignmentMode.setter
    @abstractmethod
    def AlignmentMode(self, value):
        pass

    @property
    @abstractmethod
    def Altitude(self):
        pass

    @property
    @abstractmethod
    def ApertureArea(self):
        pass

    @property
    @abstractmethod
    def ApertureDiameter(self):
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
    def CanPulseGuide(self):
        pass

    @property
    @abstractmethod
    def CanSetDeclinationRate(self):
        pass

    @property
    @abstractmethod
    def CanSetGuideRates(self):
        pass

    @property
    @abstractmethod
    def CanSetPark(self):
        pass

    @property
    @abstractmethod
    def CanSetPierSide(self):
        pass

    @property
    @abstractmethod
    def CanSetRightAscensionRate(self):
        pass

    @property
    @abstractmethod
    def CanSetTracking(self):
        pass

    @property
    @abstractmethod
    def CanSlew(self):
        pass

    @property
    @abstractmethod
    def CanSlewAltAz(self):
        pass

    @property
    @abstractmethod
    def CanSlewAltAzAsync(self):
        pass

    @property
    @abstractmethod
    def CanSlewAsync(self):
        pass

    @property
    @abstractmethod
    def CanSync(self):
        pass

    @property
    @abstractmethod
    def CanSyncAltAz(self):
        pass

    @property
    @abstractmethod
    def CanUnpark(self):
        pass

    @property
    @abstractmethod
    def Declination(self):
        pass

    @Declination.setter
    @abstractmethod
    def Declination(self, value):
        pass

    @property
    @abstractmethod
    def DeclinationRate(self):
        pass

    @DeclinationRate.setter
    @abstractmethod
    def DeclinationRate(self, value):
        pass

    @property
    @abstractmethod
    def DoesRefraction(self):
        pass

    @DoesRefraction.setter
    @abstractmethod
    def DoesRefraction(self, value):
        pass

    @property
    @abstractmethod
    def EquatorialSystem(self):
        pass

    @property
    @abstractmethod
    def FocalLength(self):
        pass

    @property
    @abstractmethod
    def GuideRateDeclination(self):
        pass

    @GuideRateDeclination.setter
    @abstractmethod
    def GuideRateDeclination(self, value):
        pass

    @property
    @abstractmethod
    def GuideRateRightAscension(self):
        pass

    @GuideRateRightAscension.setter
    @abstractmethod
    def GuideRateRightAscension(self, value):
        pass

    @property
    @abstractmethod
    def IsPulseGuiding(self):
        pass

    @property
    @abstractmethod
    def RightAscension(self):
        pass

    @property
    @abstractmethod
    def RightAscensionRate(self):
        pass

    @RightAscensionRate.setter
    @abstractmethod
    def RightAscensionRate(self, value):
        pass

    @property
    @abstractmethod
    def SideOfPier(self):
        pass

    @SideOfPier.setter
    @abstractmethod
    def SideOfPier(self, value):
        pass

    @property
    @abstractmethod
    def SiderealTime(self):
        pass

    @property
    @abstractmethod
    def SiteElevation(self):
        pass

    @SiteElevation.setter
    @abstractmethod
    def SiteElevation(self, value):
        pass

    @property
    @abstractmethod
    def SiteLatitude(self):
        pass

    @SiteLatitude.setter
    @abstractmethod
    def SiteLatitude(self, value):
        pass

    @property
    @abstractmethod
    def SiteLongitude(self):
        pass

    @property
    @abstractmethod
    def Slewing(self):
        pass

    @property
    @abstractmethod
    def SlewSettleTime(self):
        pass

    @SlewSettleTime.setter
    @abstractmethod
    def SlewSettleTime(self, value):
        pass

    @property
    @abstractmethod
    def TargetDeclination(self):
        pass

    @TargetDeclination.setter
    @abstractmethod
    def TargetDeclination(self, value):
        pass

    @property
    @abstractmethod
    def TargetRightAscension(self):
        pass

    @TargetRightAscension.setter
    @abstractmethod
    def TargetRightAscension(self, value):
        pass

    @property
    @abstractmethod
    def Tracking(self):
        pass

    @Tracking.setter
    @abstractmethod
    def Tracking(self, value):
        pass

    @property
    @abstractmethod
    def TrackingRate(self):
        pass

    @TrackingRate.setter
    @abstractmethod
    def TrackingRate(self, value):
        pass

    @property
    @abstractmethod
    def TrackingRates(self):
        pass

    @property
    @abstractmethod
    def UTCDate(self):
        pass

    @UTCDate.setter
    @abstractmethod
    def UTCDate(self, value):
        pass
