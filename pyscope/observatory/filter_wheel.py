from abc import ABC, abstractmethod

from ..utils._docstring_inheritee import _DocstringInheritee


class FilterWheel(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract base class for filter wheel devices.

        This class defines the common interface for filter wheel devices, including properties
        for focus off sets, filter names, and the current filter positon. Subclasses must implement
        the abstract methods and properties defined here.

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
    def FocusOffsets(self):
        """
        Focus offsets for each filter in the wheel. (`list` of `int`)

        0-indexed list of offsets, one offset per valid slot number.
        Values are focuser and filter dependant, and are typically set up by standardizations (such as ASCOM) or by the user.
        If focuser offsets aren't available, all values will be 0.
        """
        pass

    @property
    @abstractmethod
    def Names(self):
        """
        Name of each filter in the wheel. (`list` of `str`)

        0-indexed list of filter names, one name per valid slot number.
        Values are typically set up by standardizations (such as ASCOM) or by the user.
        If filter names aren't available, all values will be "FilterX" such that 1 <= X <= N.
        """
        pass

    @property
    @abstractmethod
    def Position(self):
        """
        The current filter wheel position. (`int`)

        Given as the current slot number, of -1 if wheel is moving.
        During motion, a position of -1 is mandatory, no valid slot numbers must be returned during rotation past filter positions.
        """
        pass

    @Position.setter
    @abstractmethod
    def Position(self, value):
        pass
