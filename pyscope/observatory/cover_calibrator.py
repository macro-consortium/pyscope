from abc import ABC, abstractmethod

from ..utils._docstring_inheritee import _DocstringInheritee


class CoverCalibrator(ABC, metaclass=_DocstringInheritee):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract base class for a cover calibrator device.

        Defines the common interface for cover calibrator devices, including methods
        for controlling the cover and calibrator light. Subclasses must implement the
        abstract methods and properties in this class.

        Parameters
        ----------
        *args : `tuple`
            Variable length argument list.
        **kwargs : `dict`
            Arbitrary keyword arguments.
        """
        pass

    @abstractmethod
    def CalibratorOff(self):
        """
        Turns calibrator off if the device has a calibrator.

        If the calibrator requires time to safely stabilise, `CalibratorState` must show that the calibrator is not ready yet.
        When the calibrator has stabilised, `CalibratorState` must show that the calibrator is ready and off.
        If a device has both cover and calibrator capabilities, the method will return `CoverState` to its original status before `CalibratorOn` was called.
        An error condition arising while turning off the calibrator must be indicated in `CalibratorState`.
        """
        pass

    @abstractmethod
    def CalibratorOn(self, Brightness):
        """
        Turns the calibrator on at the specified brightness if the device has a calibrator.

        If the calibrator requires time to safely stabilise, `CalibratorState` must show that the calibrator is not ready yet.
        When the calibrator has stabilised, `CalibratorState` must show that the calibrator is ready and on.
        If a device has both cover and calibrator capabilities, the method may change `CoverState`.
        An error condition arising while turning on the calibrator must be indicated in `CalibratorState`.

        Parameters
        ----------
        Brightness : `int`
            The illumination brightness to set the calibrator at in the range 0 to `MaxBrightness`.
        """
        pass

    @abstractmethod
    def CloseCover(self):
        """
        Starts closing the cover if the device has a cover.

        While the cover is closing, `CoverState` must show that the cover is moving.
        When the cover is fully closed, `CoverState` must show that the cover is closed.
        If an error condition arises while closing the cover, it must be indicated in `CoverState`.
        """
        pass

    @abstractmethod
    def HaltCover(self):
        """
        Stops any present cover movement if the device has a cover and cover movement can be halted.

        Stops cover movement as soon as possible and sets `CoverState` to an appropriate value such as open or closed.
        """
        pass

    @abstractmethod
    def OpenCover(self):
        """
        Starts opening the cover if the device has a cover.

        While the cover is opening, `CoverState` must show that the cover is moving.
        When the cover is fully open, `CoverState` must show that the cover is open.
        If an error condition arises while opening the cover, it must be indicated in `CoverState`.
        """
        pass

    @property
    @abstractmethod
    def Brightness(self):
        """
        The current calibrator brightness in the range of 0 to `MaxBrightness`. (`int`)

        The brightness must be 0 if the `CalibratorState` is `Off`.
        """
        pass

    @property
    @abstractmethod
    def CalibratorState(self):
        """
        The state of the calibrator device, if present, otherwise indicate that it does not exist. (`enum`)

        When the calibrator is changing the state must indicate that the calibrator is busy.
        If the device is unaware of the calibrator state, such as if hardware doesn't report the state and the calibrator was just powered on, it must indicate as such.
        Users should be able to carry out commands like `CalibratorOn` and `CalibratorOff` regardless of this unknown state.
        Enum values representing states is determined by the device manufacturer or driver author.
        """
        pass

    @property
    @abstractmethod
    def CoverState(self):
        """
        The state of the cover device, if present, otherwise indicate that it does not exist. (`enum`)

        When the cover is changing the state must indicate that the cover is busy.
        If the device is unaware of the cover state, such as if hardware doesn't report the state and the cover was just powered on, it must indicate as such.
        Users should be able to carry out commands like `OpenCover`, `CloseCover`, and `HaltCover` regardless of this unknown state.
        """
        pass

    @property
    @abstractmethod
    def MaxBrightness(self):
        """
        Brightness value that makes the calibrator produce the maximum illumination supported. (`int`)

        A value of 1 indicates that the calibrator can only be off or on.
        A value of any other X should indicate that the calibrator has X discreet brightness levels in addition to off (0).
        Value determined by the device manufacturer or driver author based on hardware capabilities.
        """
        pass
