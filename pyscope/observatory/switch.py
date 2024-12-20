from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class Switch(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract base class for switch devices.

        This class defines the common interface for switch devices, including methods for
        getting and setting switch values, and getting switch names and descriptions.
        Subclasses must implement the abstract methods and properties in this class.

        Parameters
        ----------
        *args : `tuple`
            Variable length argument list.
        **kwargs : `dict`
            Arbitrary keyword arguments.
        """
        pass

    @abstractmethod
    def CanWrite(self, ID):
        """
        Whether the switch can be written to. (`bool`)

        Most devices will return `True` for this property, but some switches are
        meant to be read-only, such as limit switches or sensors.

        Parameters
        ----------
        ID : `int`
            The switch ID number.
        """
        pass

    @abstractmethod
    def GetSwitch(self, ID):
        """
        The current state of the switch as a boolean. (`bool`)

        This is a mandatory property for all switch devices. For multi-state switches,
        this should be `True` for when the device is at the maximum value, `False` if at minimum,
        and either `True` or `False` for intermediate values; specification up to driver author.

        Parameters
        ----------
        ID : `int`
            The switch ID number.
        """
        pass

    @abstractmethod
    def GetSwitchDescription(self, ID):
        """
        The detailed description of the switch, to be used for features such as tooltips. (`str`)
        
        Parameters
        ----------
        ID : `int`
            The switch ID number.
        """
        pass

    @abstractmethod
    def GetSwitchName(self, ID):
        """
        The name of the switch, to be used for display purposes. (`str`)

        Parameters
        ----------
        ID : `int`
            The switch ID number.
        """
        pass

    @abstractmethod
    def MaxSwitchValue(self, ID):
        """
        The maximum value of the switch. (`float`)

        Must be greater than `MinSwitchValue`. Two-state devices should return 1.0, and only
        multi-state devices should return values greater than 1.0.

        Parameters
        ----------
        ID : `int`
            The switch ID number.
        """
        pass

    @abstractmethod
    def MinSwitchValue(self, ID):
        """
        The minimum value of the switch. (`float`)

        Must be less than `MaxSwitchValue`. Two-state devices should return 0.0.
        """
        pass

    @abstractmethod
    def SetSwitch(self, ID, State):
        """
        Sets the state of the switch controller device.

        `GetSwitchValue` will also be set, to `MaxSwitchValue` if `State` is `True`, and `MinSwitchValue` if `State` is `False`.

        Parameters
        ----------
        ID : `int`
            The switch ID number.
        State : `bool`
            The state to set the switch to.
        """
        pass

    @abstractmethod
    def SetSwitchName(self, ID, Name):
        """
        Sets the name of the switch device.

        Parameters
        ----------
        ID : `int`
            The switch ID number.
        Name : `str`
            The new name to set the switch to.
        """
        pass

    @abstractmethod
    def SetSwitchValue(self, ID, Value):
        """
        Sets the value of the switch device.

        Values should be between `MinSwitchValue` and `MaxSwitchValue`. If the value is
        intermediate in relation to `SwitchStep`, it will be set to an achievable value.
        How this achieved value is determined is up to the driver author.

        Parameters
        ----------
        ID : `int`
            The switch ID number.
        Value : `float`
            The value to set the switch to.
        """
        pass

    @abstractmethod
    def SwitchStep(self, ID):
        """
        The step size that the switch device supports. (`float`)

        Has to be greater than zero. This is the smallest increment that the switch device's value can be set to.
        For two-state devices, this should be 1.0, and anything else other than 0 for multi-state devices.

        Parameters
        ----------
        ID : `int`
            The switch ID number.
        """
        pass

    @property
    @abstractmethod
    def MaxSwitch(self):
        """The number of switch devices managed by this driver. (`int`)"""
        pass
