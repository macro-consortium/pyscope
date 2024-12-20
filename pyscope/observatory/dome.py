from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class Dome(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract base class for dome devices.

        This class defines the common interface for dome devices, including methods for controlling
        the dome's movement and shutter. Subclasses must implement the abstract methods and properties
        in this class.

        Parameters
        ----------
        *args : `tuple`
            Variable length argument list.
        **kwargs : `dict`
            Arbitrary keyword arguments.
        """
        pass

    @abstractmethod
    def AbortSlew(self):
        """
        Immediately stop any dome movement.

        This method will disable hardware slewing immediately, and sets `Slaved` to `False`.
        """
        pass

    @abstractmethod
    def CloseShutter(self):
        """Closes the shutter."""
        pass

    @abstractmethod
    def FindHome(self):
        """
        Starts searching for the dome home position.

        The method and the homing operation should be able to run asynchronously, meaning
        that any additional `FindHome` method calls shouldn't block current homing.
        After the homing is complete, the `AtHome` property should be set to `True`, and the `Azimuth` synchronized to the appropriate value.
        """
        pass

    @abstractmethod
    def OpenShutter(self):
        """Opens the shutter."""
        pass

    @abstractmethod
    def Park(self):
        """
        Move the dome to the park position along the dome azimuth axis.
        
        Sets the `AtPark` property to `True` after completion, and should raise an error if `Slaved`.
        """
        pass

    @abstractmethod
    def SetPark(self):
        """Sets the current azimuth position as the park position."""
        pass

    @abstractmethod
    def SlewToAltitude(self, Altitude):
        """
        Slews the dome to the specified altitude.

        The method and the slewing operation should be able to run asynchronously, meaning
        that any additional `SlewToAltitude` method calls shouldn't block current slewing.

        Parameters
        ----------
        Altitude : `float`
            The altitude to slew to in degrees.
        """
        pass

    @abstractmethod
    def SlewToAzimuth(self, Azimuth):
        """
        Slews the dome to the specified azimuth.

        The method and the slewing operation should be able to run asynchronously, meaning
        that any additional `SlewToAzimuth` method calls shouldn't block current slewing.

        Parameters
        ----------
        Azimuth : `float`
            The azimuth to slew to in degrees, North-referenced, CW.
        """
        pass

    @abstractmethod
    def SyncToAzimuth(self, Azimuth):
        """
        Synchronizes the dome azimuth counter to the specified value.

        Parameters
        ----------
        Azimuth : `float`
            The azimuth to synchronize to in degrees, North-referenced, CW.
        """
        pass

    @property
    @abstractmethod
    def Altitude(self):
        """
        Altitude of the part of the sky that the observer is planning to observe. (`float`)

        Driver should determine how to best locate the dome aperture in order to expose the desired part of the sky,
        meaning it must consider all shutters, clamshell segments, or roof mechanisms present in the dome
        to determine the required aperture.

        Raises error if there's no altitude control.
        If altitude can not be read, returns the altitude of the last slew position.
        """
        pass

    @property
    @abstractmethod
    def AtHome(self):
        """
        Whether the dome is in the home position. (`bool`)

        Normally used post `FindHome` method call.
        Value is reset to `False` after any slew operation, except if the slewing just so happens to request the home position.
        If the dome hardware is capable of detecting when slewing "passes by" the home position,
        `AtHome` may become `True` during that slewing.
        Due to some devices holding a small range of azimuths as the home position, or due to accuracy losses
        from dome inertia, resolution of the home position sensor, the azimuth encoder, and/or floating point errors,
        applications shouldn't assume sensed azimuths will be identical each time `AtHome` is `True`.
        """
        pass

    @property
    @abstractmethod
    def AtPark(self):
        """
        Whether the dome is in the park position. (`bool`)

        Unlike `AtHome`, `AtPark` is explicitly only set after a `Park` method call,
        and is reset with any slew operation.
        Due to some devices holding a small range of azimuths as the park position, or due to accuracy losses
        from dome inertia, resolution of the park position sensor, the azimuth encoder, and/or floating point errors,
        applications shouldn't assume sensed azimuths will be identical each time `AtPark` is `True`.
        """
        pass

    @property
    @abstractmethod
    def Azimuth(self):
        """
        Current azimuth of the dome. (`float`)

        If the azimuth can not be read, returns the azimuth of the last slew position.
        """
        pass

    @property
    @abstractmethod
    def CanFindHome(self):
        """Whether the dome can find the home position, i.e. is it capable of `FindHome`. (`bool`)"""
        pass

    @property
    @abstractmethod
    def CanPark(self):
        """Whether the dome can park, i.e. is it capable of `Park`. (`bool`)"""
        pass

    @property
    @abstractmethod
    def CanSetAltitude(self):
        """Whether the dome can set the altitude, i.e. is it capable of `SlewToAltitude`. (`bool`)"""
        pass

    @property
    @abstractmethod
    def CanSetAzimuth(self):
        """
        Whether the dome can set the azimuth, i.e. is it capable of `SlewToAzimuth`. (`bool`)
        
        In simpler terms, whether the dome is equipped with rotation control or not.
        """
        pass

    @property
    @abstractmethod
    def CanSetPark(self):
        """Whether the dome can set the park position, i.e. is it capable of `SetPark`. (`bool`)"""
        pass

    @property
    @abstractmethod
    def CanSetShutter(self):
        """Whether the dome can set the shutter state, i.e. is it capable of `OpenShutter` and `CloseShutter`. (`bool`)"""
        pass

    @property
    @abstractmethod
    def CanSlave(self):
        """
        Whether the dome can be slaved to a telescope, i.e. is it capable of `Slaved` states. (`bool`)
        
        This should only be `True` if the dome has its own slaving mechanism;
        a dome driver should not query a telescope driver directly.
        """
        pass

    @property
    @abstractmethod
    def CanSyncAzimuth(self):
        """Whether the dome can synchronize the azimuth, i.e. is it capable of `SyncToAzimuth`. (`bool`)"""
        pass

    @property
    @abstractmethod
    def ShutterStatus(self):
        """
        The status of the dome shutter or roof structure. (`enum`)

        Raises error if there's no shutter control, or if the shutter status can not be read, returns the last shutter state.
        Enum values and their representations are defined by the driver.
        See :py:attr:`ASCOMDome.ShutterStatus` for an example.
        """
        pass

    @property
    @abstractmethod
    def Slaved(self):
        """
        Whether the dome is currently slaved to a telescope. (`bool`)
        
        During operations, set to `True` to enable hardware slewing, if capable, see `CanSlave`.
        """
        pass

    @property
    @abstractmethod
    def Slewing(self):
        """Whether the dome is currently slewing in any direction. (`bool`)"""
        pass
