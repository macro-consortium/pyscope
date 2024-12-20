from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class Rotator(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract base class for a rotator device.

        This class defines the interface for a rotator device, including methods for
        moving the rotator, halting movement, and properties for determining the current
        position and movement state of the rotator. Subclasses must implement the abstract
        methods and properties in this class.

        Parameters
        ----------
        *args : `tuple`
            Variable length argument list.
        **kwargs : `dict`
            Arbitrary keyword arguments.
        """
        pass

    @abstractmethod
    def Halt(self):
        """Immediately stop any movement of the rotator due to a `Move` or `MoveAbsolute` call."""
        pass

    @abstractmethod
    def Move(self, Position):
        """
        Move the rotator `Position` degrees from the current position.

        Calling will change `TargetPosition` to sum of the current angular position and `Position` module 360 degrees.

        Parameters
        ----------
        Position : `float`
            Relative position to move from current `Position`, in degrees
        """
        pass

    @abstractmethod
    def MoveAbsolute(self, Position):
        """
        Move the rotator to the absolute `Position` degrees.

        Calling will change `TargetPosition` to `Position`.

        Parameters
        ----------
        Position : `float`
            Absolute position to move to, in degrees
        """
        pass

    @abstractmethod
    def MoveMechanical(self, Position):
        """
        Move the rotator to the mechanical `Position` angle.

        This move is independent of any sync offsets, and is to be used for circumstances
        where physical rotaion angle is needed (i.e. taking sky flats).
        For instances such as imaging, `MoveAbsolute` should be preferred.

        Parameters
        ----------
        Position : `float`
            Mechanical position to move to, in degrees
        """
        pass

    @abstractmethod
    def Sync(self, Position):
        """
        Synchronize the rotator to the `Position` angle without movement.

        Once set, along with determining sync offsets, `MoveAbsolute` and `Position` must function
        in terms of synced coordinates rather than mechanical.
        Implementations should make sure offsets persist across driver starts and device reboots.

        Parameters
        ----------
        Position : `float`
            Sync position to set, in degrees
        """
        pass

    @property
    @abstractmethod
    def CanReverse(self):
        """Whether the rotator supports the `Reverse` method. (`bool`)"""
        pass

    @property
    @abstractmethod
    def IsMoving(self):
        """Whether the rotator is currently moving. (`bool`)"""
        pass

    @property
    @abstractmethod
    def MechanicalPosition(self):
        """The current mechanical position of the rotator, in degrees. (`float`)"""
        pass

    @property
    @abstractmethod
    def Position(self):
        """The current angular position of the rotator accounting offsets, in degrees. (`float`)"""
        pass

    @property
    @abstractmethod
    def Reverse(self):
        """
        Whether the rotator is in reverse mode. (`bool`)
        
        If `True`, the rotation and angular direction must be reversed for optics.
        """
        pass

    @Reverse.setter
    @abstractmethod
    def Reverse(self, value):
        pass

    @property
    @abstractmethod
    def StepSize(self):
        """The minimum step size of the rotator, in degrees. (`float`)"""
        pass

    @property
    @abstractmethod
    def TargetPosition(self):
        """
        The target angular position of the rotator, in degrees. (`float`)
        
        Upon a `Move` or `MoveAbsolute` call, this property is set to the position angle to which
        the rotator is moving. Value persists until another move call.
        """
        pass
