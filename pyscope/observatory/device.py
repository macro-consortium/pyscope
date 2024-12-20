from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class Device(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract base class for all deivce types.

        This class defines the common interface for all devices.
        Includes connection status and device name properties. Subclasses must implement the
        abstract methods and properties in this class.

        Parameters
        ----------
        *args : `tuple`
            Variable length argument list.
        **kwargs : `dict`
            Arbitrary keyword arguments.
        """
        pass

    @property
    @abstractmethod
    def Connected(self):
        """Whether the device is connected or not. (`bool`)"""
        pass

    @Connected.setter
    @abstractmethod
    def Connected(self, value):
        pass

    @property
    @abstractmethod
    def Name(self):
        """The shorthand name of the device for display only. (`str`)"""
        pass
