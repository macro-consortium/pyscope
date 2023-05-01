from . import Driver
from .. import abstract

class Telescope(Driver, abstract.Telescope):
    def AbortSlew(self):
        self._com_object.AbortSlew()
    
    def AxisRates(self, Axis):
        return self._com_object.AxisRates(Axis)
    
    def CanMoveAxis(self, Axis):
        return self._com_object.CanMoveAxis(Axis)
    
    def Choose(self, TelescopeID):
        self._com_object.Choose(TelescopeID)

    def DestinationSideOfPier(self, RightAscension, Declination):
        return self._com_object.DestinationSideOfPier(RightAscension, Declination)
    
    def FindHome(self):
        self._com_object.FindHome()
    
    def MoveAxis(self, Axis, Rate):
        self._com_object.MoveAxis(Axis, Rate)
    
    def Park(self):
        self._com_object.Park()
    
    def PulseGuide(self, Direction, Duration):
        self._com_object.PulseGuide(Direction, Duration)
    
    def SetPark(self):
        self._com_object.SetPark()
    
    def SlewToAltAz(self, Azimuth, Altitude):
        self._com_object.SlewToAltAz(Azimuth, Altitude)
    
    def SlewToAltAzAsync(self, Azimuth, Altitude):
        self._com_object.SlewToAltAzAsync(Azimuth, Altitude)
    
    def SlewToCoordinates(self, RightAscension, Declination):
        self._com_object.SlewToCoordinates(RightAscension, Declination)
    
    def SlewToCoordinatesAsync(self, RightAscension, Declination):
        self._com_object.SlewToCoordinatesAsync(RightAscension, Declination)
    
    def SlewToTarget(self):
        self._com_object.SlewToTarget()
    
    def SlewToTargetAsync(self):
        self._com_object.SlewToTargetAsync()
    
    def SyncToAltAz(self, Azimuth, Altitude):
        self._com_object.SyncToAltAz(Azimuth, Altitude)
    
    def SyncToCoordinates(self, RightAscension, Declination):
        self._com_object.SyncToCoordinates(RightAscension, Declination)
    
    def SyncToTarget(self):
        self._com_object.SyncToTarget()
    
    def Unpark(self):
        self._com_object.Unpark()
    
    @property
    def AlignmentMode(self):
        return self._com_object.AlignmentMode

    @property
    def Altitude(self):
        return self._com_object.Altitude
    
    @property
    def ApertureArea(self):
        return self._com_object.ApertureArea
    
    @property
    def ApertureDiameter(self):
        return self._com_object.ApertureDiameter
    
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
    
    def CanPulseGuide(self, Direction):
        return self._com_object.CanPulseGuide(Direction)
    
    @property
    def CanSetDeclinationRate(self):
        return self._com_object.CanSetDeclinationRate
    
    @property
    def CanSetGuideRates(self):
        return self._com_object.CanSetGuideRates
    
    @property
    def CanSetPark(self):
        return self._com_object.CanSetPark
    
    @property
    def CanSetPierSide(self):
        return self._com_object.CanSetPierSide
    
    @property
    def CanSetRightAscensionRate(self):
        return self._com_object.CanSetRightAscensionRate
    
    @property
    def CanSetTracking(self):
        return self._com_object.CanSetTracking
    
    @property
    def CanSlew(self):
        return self._com_object.CanSlew
    
    @property
    def CanSlewAltAz(self):
        return self._com_object.CanSlewAltAz
    
    @property
    def CanSlewAltAzAsync(self):
        return self._com_object.CanSlewAltAzAsync
    
    @property
    def CanSlewAsync(self):
        return self._com_object.CanSlewAsync
    
    @property
    def CanSync(self):
        return self._com_object.CanSync

    @property
    def CanSyncAltAz(self):
        return self._com_object.CanSyncAltAz
    
    @property
    def CanUnpark(self):
        return self._com_object.CanUnpark
    
    @property
    def Declination(self):
        return self._com_object.Declination
    
    @property
    def DeclinationRate(self):
        return self._com_object.DeclinationRate
    @DeclinationRate.setter
    def DeclinationRate(self, value):
        self._com_object.DeclinationRate = value

    @property
    def DoesRefraction(self):
        return self._com_object.DoesRefraction
    @DoesRefraction.setter
    def DoesRefraction(self, value):
        self._com_object.DoesRefraction = value
    
    @property
    def EquatorialSystem(self):
        return self._com_object.EquatorialSystem
    
    @property
    def FocalLength(self):
        return self._com_object.FocalLength

    @property
    def GuideRateDeclination(self):
        return self._com_object.GuideRateDeclination
    @GuideRateDeclination.setter
    def GuideRateDeclination(self, value):
        self._com_object.GuideRateDeclination = value

    @property
    def GuideRateRightAscension(self):
        return self._com_object.GuideRateRightAscension
    @GuideRateRightAscension.setter
    def GuideRateRightAscension(self, value):
        self._com_object.GuideRateRightAscension = value

    @property
    def IsPulseGuiding(self):
        return self._com_object.IsPulseGuiding
    
    @property
    def RightAscension(self):
        return self._com_object.RightAscension

    @property
    def RightAscensionRate(self):
        return self._com_object.RightAscensionRate
    @RightAscensionRate.setter
    def RightAscensionRate(self, value):
        self._com_object.RightAscensionRate = value

    @property
    def SideOfPier(self):
        return self._com_object.SideOfPier
    @SideOfPier.setter
    def SideOfPier(self, value):
        self._com_object.SideOfPier = value
    
    @property
    def SiderealTime(self):
        return self._com_object.SiderealTime

    @property
    def SiteElevation(self):
        return self._com_object.SiteElevation
    @SiteElevation.setter
    def SiteElevation(self, value):
        self._com_object.SiteElevation = value
    
    @property
    def SiteLatitude(self):
        return self._com_object.SiteLatitude
    @SiteLatitude.setter
    def SiteLatitude(self, value):
        self._com_object.SiteLatitude = value
    
    @property
    def SiteLongitude(self):
        return self._com_object.SiteLongitude
    @SiteLongitude.setter
    def SiteLongitude(self, value):
        self._com_object.SiteLongitude = value
    
    @property
    def Slewing(self):
        return self._com_object.Slewing
    
    @property
    def SlewSettleTime(self):
        return self._com_object.SlewSettleTime
    @SlewSettleTime.setter
    def SlewSettleTime(self, value):
        self._com_object.SlewSettleTime = value
    
    @property
    def TargetDeclination(self):
        return self._com_object.TargetDeclination
    @TargetDeclination.setter
    def TargetDeclination(self, value):
        self._com_object.TargetDeclination = value
    
    @property
    def TargetRightAscension(self):
        return self._com_object.TargetRightAscension
    @TargetRightAscension.setter
    def TargetRightAscension(self, value):
        self._com_object.TargetRightAscension = value
    
    @property
    def Tracking(self):
        return self._com_object.Tracking
    @Tracking.setter
    def Tracking(self, value):
        self._com_object.Tracking = value
    
    @property
    def TrackingRate(self):
        return self._com_object.TrackingRate
    @TrackingRate.setter
    def TrackingRate(self, value):
        self._com_object.TrackingRate = value
    
    @property
    def TrackingRates(self):
        return self._com_object.TrackingRates
    
    @property
    def UTCDate(self):
        return self._com_object.UTCDate
    @UTCDate.setter
    def UTCDate(self, value):
        self._com_object.UTCDate = value