from abc import ABC, abstractmethod

from ..utils._docstring_inheritee import _DocstringInheritee


class Focuser(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract base class for focuser devices.

        This class defines the common interface for focusr devices, including methods for halting and moving the focuser,
        as well as properties for various attributes. Subcalsses must implement the methods and properties
        defined in the class.

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
        """
        Immediately stop focuser motion due to any previous `Move` call.

        Some focusers may not support this function, and as such must implement an exception raise.
        Any host software implementing the method should call the method upon initilization, and signify that
        halting is not supported if an exception is raised (such as graying out the Halt button).
        """
        pass

    @abstractmethod
    def Move(self, Position):
        """
        Moves the focuser either by the specified amount or to the specified position, based on the `Absolute` property.

        If the `Absolute` property is `True`, then the focuser should move to an exact step position, and the given `Position` parameter should be
        an integer between 0 and `MaxStep`. If the `Absolute` property is `False`, then the focuser should move relatively by the given `Position` parameter,
        which should be an integer between -`MaxIncrement` and `MaxIncrement`.

        Parameters
        ----------
        Position : `int`
            The position to move to, or the amount to move relatively.
        """
        pass

    @property
    @abstractmethod
    def Absolute(self):
        """Whether the focuser is capable of absolute position, i.e. move to a specific step position. (`bool`)"""
        pass

    @Absolute.setter
    @abstractmethod
    def Absolute(self, value):
        pass

    @property
    @abstractmethod
    def IsMoving(self):
        """Whether the focuser is currently moving. (`bool`)"""
        pass

    @property
    @abstractmethod
    def MaxIncrement(self):
        """
        The maximum increment size allowed by the focuser. (`int`)

        In other words, the maximum number of steps allowed in a single move operation.
        For most focuser devices, this value is the same as the `MaxStep` property, and is normally used to limit
        the increment size in relation to displaying in the host software.
        """
        pass

    @property
    @abstractmethod
    def MaxStep(self):
        """
        Maximum step position allowed by the focuser. (`int`)

        The focuser supports stepping between 0 and this value.
        An attempt to move the focuser beyond this limit should result in the move stopping at the limit.
        """
        pass

    @property
    @abstractmethod
    def Position(self):
        """
        Current focuser position in steps. (`int`)

        Should only be valid if absolute positioning is supported, i.e. the `Absolute` property is `True`.
        """
        pass

    @property
    @abstractmethod
    def StepSize(self):
        """Step size for the focuser in microns. (`float`)"""
        pass

    @property
    @abstractmethod
    def TempComp(self):
        """
        State of the temperature compensation mode. (`bool`)

        Is always `False` if the focuser does not support temperature compensation.
        Setting `TempComp` to `True` enables temperature tracking of the focuser, and setting it to `False` should disable that tracking.
        An attempt at setting `TempComp` while `TempCompAvailable` is `False` should result in an exception.
        """
        pass

    @TempComp.setter
    @abstractmethod
    def TempComp(self, value):
        pass

    @property
    @abstractmethod
    def TempCompAvailable(self):
        """
        Whether the focuser has temperature compensation available. (`bool`)

        Only `True` if the focuser's temperature compsensation can be set via `TempComp`.
        """
        pass

    @property
    @abstractmethod
    def Temperature(self):
        """
        Current ambient temperature measured by the focuser in degrees Celsius. (`float`)

        Raises exception if focuser not equipped to measure ambient temperature.
        Most focusers with `TempCompAvailable` set to `True` should have this property available, but not all.
        """
        pass

    @Temperature.setter
    @abstractmethod
    def Temperature(self, value):
        pass
