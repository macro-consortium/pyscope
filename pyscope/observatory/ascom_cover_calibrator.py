import logging

from .ascom_device import ASCOMDevice
from .cover_calibrator import CoverCalibrator

logger = logging.getLogger(__name__)


class ASCOMCoverCalibrator(ASCOMDevice, CoverCalibrator):
    def __init__(self, identifier, alpaca=False, device_number=0, protocol="http"):
        """
        ASCOM implementation of the :py:meth:`CoverCalibrator` abstract base class.

        Provides the functionality to control an ASCOM-compatible cover calibrator device,
        including methods for controlling the cover and calibrator light.

        Parameters
        ----------
        identifier : `str`
            The device identifier.
        alpaca : `bool`, default : `False`, optional
            Whether the device is an Alpaca device.
        device_number : `int`, default : 0, optional
            The device number.
        protocol : `str`, default : "http", optional
            The communication protocol to use.
        """
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    def CalibratorOff(self):
        """
        Turns calibrator off if the device has a calibrator.

        If the calibrator requires time to safely stabilise, `CalibratorState` must return `NotReady`.
        When the calibrator has stabilised, `CalibratorState` must return `Off`.
        If a device has both cover and calibrator capabilities, the method will return `CoverState` to its original status before `CalibratorOn` was called.
        If an error condition arises while turning off the calibrator, `CalibratorState` must return `Error`.
        """
        logger.debug(f"ASCOMCoverCalibrator.CalibratorOff() called")
        self._device.CalibratorOff()

    def CalibratorOn(self, Brightness):
        """
        Turns the calibrator on at the specified brightness if the device has a calibrator.
        
        If the calibrator requires time to safely stabilise, `CalibratorState` must return `NotReady`.
        When the calibrator has stabilised, `CalibratorState` must return `Ready`.
        If a device has both cover and calibrator capabilities, the method may change `CoverState`.
        If an error condition arises while turning on the calibrator, `CalibratorState` must return `Error`.

        Parameters
        ----------
        Brightness : `int`
            The illumination brightness to set the calibrator at in the range 0 to `MaxBrightness`.
        """
        logger.debug(f"ASCOMCoverCalibrator.CalibratorOn({Brightness}) called")
        self._device.CalibratorOn(Brightness)

    def CloseCover(self):
        """
        Starts closing the cover if the device has a cover.
        
        While the cover is closing, `CoverState` must return `Moving`.
        When the cover is fully closed, `CoverState` must return `Closed`.
        If an error condition arises while closing the cover, `CoverState` must return `Error`.
        """
        logger.debug(f"ASCOMCoverCalibrator.CloseCover() called")
        self._device.CloseCover()

    def HaltCover(self):
        """
        Stops any present cover movement if the device has a cover and cover movement can be halted.
        
        Stops cover movement as soon as possible and sets `CoverState` to `Open`, `Closed`, or `Unknown` appropriately.
        """
        logger.debug(f"ASCOMCoverCalibrator.HaltCover() called")
        self._device.HaltCover()

    def OpenCover(self):
        """
        Starts opening the cover if the device has a cover.

        While the cover is opening, `CoverState` must return `Moving`.
        When the cover is fully open, `CoverState` must return `Open`.
        If an error condition arises while opening the cover, `CoverState` must return `Error`.
        """
        logger.debug(f"ASCOMCoverCalibrator.OpenCover() called")
        self._device.OpenCover()

    @property
    def Brightness(self):
        logger.debug(f"ASCOMCoverCalibrator.Brightness property called")
        return self._device.Brightness

    @property
    def CalibratorState(self):
        """
        The state of the calibrator device, if present, otherwise return `NotPresent`. (`CalibratorStatus <https://ascom-standards.org/help/developer/html/T_ASCOM_DeviceInterface_CalibratorStatus.htm>`_)

        When the calibrator is changing the state must be `NotReady`.
        If the device is unaware of the calibrator state, such as if hardware doesn't report the state and the calibrator was just powered on, the state must be `Unknown`.
        Users should be able to carry out commands like `CalibratorOn` and `CalibratorOff` regardless of this unknown state.

        Returns
        -------
        `CalibratorStatus`
            The state of the calibrator device in the following representations:
                * 0 : `NotPresent`, the device has no calibrator.
                * 1 : `Off`, the calibrator is off.
                * 2 : `NotReady`, the calibrator is stabilising or hasn't finished the last command.
                * 3 : `Ready`, the calibrator is ready.
                * 4 : `Unknown`, the state is unknown.
                * 5 : `Error`, an error occurred while changing states.
        """
        logger.debug(f"ASCOMCoverCalibrator.CalibratorState property called")
        return self._device.CalibratorState

    @property
    def CoverState(self):
        """
        The state of the cover device, if present, otherwise return `NotPresent`. (`CoverStatus <https://ascom-standards.org/help/developer/html/T_ASCOM_DeviceInterface_CoverStatus.htm>`_)
        
        When the cover is changing the state must be `Moving`.
        If the device is unaware of the cover state, such as if hardware doesn't report the state and the cover was just powered on, the state must be `Unknown`.
        Users should be able to carry out commands like `OpenCover`, `CloseCover`, and `HaltCover` regardless of this unknown state.
        
        Returns
        -------
        `CoverStatus`
            The state of the cover device in the following representations:
                * 0 : `NotPresent`, the device has no cover.
                * 1 : `Closed`, the cover is closed.
                * 2 : `Moving`, the cover is moving.
                * 3 : `Open`, the cover is open.
                * 4 : `Unknown`, the state is unknown.
                * 5 : `Error`, an error occurred while changing states.
        """
        logger.debug(f"ASCOMCoverCalibrator.CoverState property called")
        return self._device.CoverState

    @property
    def MaxBrightness(self):
        logger.debug(f"ASCOMCoverCalibrator.MaxBrightness property called")
        return self._device.MaxBrightness
