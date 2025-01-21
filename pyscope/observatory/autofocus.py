from abc import ABC, abstractmethod

from ._docstring_inheritee import _DocstringInheritee


class Autofocus(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract base class for autofocus functionality on different utility platforms.

        This class provides a common interface for autofocus functionality, including the
        bare minimum for any platform such as initialization, running the autofocus routine,
        and aborting the autofocus routine.
        Example platforms include Maxim, PWI, PWI4, etc.
        Args and kwargs provide needed parameters to the platform-specific autofocus routine,
        such as hosting protocol and port.

        Parameters
        ----------
        *args : `tuple`
            Variable length argument list.
        **kwargs : `dict`
            Arbitrary keyword arguments.
        """
        pass

    @abstractmethod
    def Run(self, *args, **kwargs):
        """
        Run the autofocus routine on the given platform.
        Args and kwargs provide needed parameters to the platform-specific autofocus routine,
        such as exposure time and timeout.

        Parameters
        ----------
        *args : `tuple`
            Variable length argument list.
        **kwargs : `dict`
            Arbitrary keyword arguments.
        """
        pass

    @abstractmethod
    def Abort(self, *args, **kwargs):
        """
        Abort the autofocus routine on the given platform.
        Whether aborting is immediate or has a gracious exit process is platform-specific.
        Args and kwargs usually should not be needed for an abort.

        Parameters
        ----------
        *args : `tuple`
            Variable length argument list.
        **kwargs : `dict`
            Arbitrary keyword arguments.
        """
        pass
