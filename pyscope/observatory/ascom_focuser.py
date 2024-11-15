import logging

from .ascom_device import ASCOMDevice
from .focuser import Focuser

logger = logging.getLogger(__name__)


class ASCOMFocuser(ASCOMDevice, Focuser):
    def __init__(self, identifier, alpaca=False, device_number=0, protocol="http"):
        """
        ASCOM implementation of the Focuser abstract base class.

        The class provides functionality to control an ASCOM-compatible focuser device,
        including methods for halting and moving the focuser, as well as properties for
        various focuser attributes.

        Parameters
        ----------
        identifier : `str`
            The device identifier.
        alpaca : `bool`, default : `False`, optional
            Flag indicating whether the device is an Alpaca device.
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

    def Halt(self):
        logger.debug(f"ASCOMFocuser.Halt() called")
        self._device.Halt()

    def Move(self, Position):
        logger.debug(f"ASCOMFocuser.Move({Position}) called")
        self._device.Move(Position)

    @property
    def Absolute(self):
        logger.debug(f"ASCOMFocuser.Absolute property called")
        return self._device.Absolute

    @property
    def IsMoving(self):
        logger.debug(f"ASCOMFocuser.IsMoving property called")
        return self._device.IsMoving

    @property
    def MaxIncrement(self):
        logger.debug(f"ASCOMFocuser.MaxIncrement property called")
        return self._device.MaxIncrement

    @property
    def MaxStep(self):
        logger.debug(f"ASCOMFocuser.MaxStep property called")
        return self._device.MaxStep

    @property
    def Position(self):
        logger.debug(f"ASCOMFocuser.Position property called")
        return self._device.Position

    @property
    def StepSize(self):
        logger.debug(f"ASCOMFocuser.StepSize property called")
        return self._device.StepSize

    @property
    def TempComp(self):
        logger.debug(f"ASCOMFocuser.TempComp property called")
        return self._device.TempComp

    @TempComp.setter
    def TempComp(self, value):
        logger.debug(f"ASCOMFocuser.TempComp property set to {value}")
        self._device.TempComp = value

    @property
    def TempCompAvailable(self):
        logger.debug(f"ASCOMFocuser.TempCompAvailable property called")
        return self._device.TempCompAvailable

    @property
    def Temperature(self):
        logger.debug(f"ASCOMFocuser.Temperature property called")
        return self._device.Temperature
