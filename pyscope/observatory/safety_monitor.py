from abc import ABC, abstractmethod

from ..utils._docstring_inheritee import _DocstringInheritee


class SafetyMonitor(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract base class for safety monitors.

        This class defines the common interface for safety monitors, a way to check if
        weather, power, and other observatory-specific conditions allow safe usage of
        observatory equipment. Subclasses must implement the abstract method in this class.

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
    def IsSafe(self):
        """Whether the observatory is safe for use. (`bool`)"""
        pass
