import logging

from .ascom_device import ASCOMDevice
from .switch import Switch

logger = logging.getLogger(__name__)


class ASCOMSwitch(ASCOMDevice, Switch):
    def __init__(
        self, identifier, alpaca=False, device_number=0, protocol="http"
    ):
        """
        ASCOM implementation of the Switch base class.

        The class provides an interface to ASCOM-compatible switch devices, including methods for
        getting and setting switch values, and getting switch names and descriptions.

        Parameters
        ----------
        identifier : `str`
            The device identifier.
        alpaca : `bool`, default : `False`, optional
            Whether the device is an Alpaca device.
        device_number : `int`, default : 0, optional
            The device number.
        protocol : `str`, default : "http", optional
            The protocol to use for communication with the device.
        """
        super().__init__(
            identifier,
            alpaca=alpaca,
            device_type=self.__class__.__name__.replace("ASCOM", ""),
            device_number=device_number,
            protocol=protocol,
        )

    def CanWrite(self, ID):
        logger.debug(f"ASCOMSwitch.CanWrite({ID}) called")
        return self._device.CanWrite(ID)

    def GetSwitch(self, ID):
        logger.debug(f"ASCOMSwitch.GetSwitch({ID}) called")
        return self._device.GetSwitch(ID)

    def GetSwitchDescription(self, ID):
        logger.debug(f"ASCOMSwitch.GetSwitchDescription({ID}) called")
        return self._device.GetSwitchDescription(ID)

    def GetSwitchName(self, ID):
        logger.debug(f"ASCOMSwitch.GetSwitchName({ID}) called")
        return self._device.GetSwitchName(ID)

    def MaxSwitchValue(self, ID):
        logger.debug(f"ASCOMSwitch.MaxSwitchValue({ID}) called")
        return self._device.MaxSwitchValue(ID)

    def MinSwitchValue(self, ID):
        logger.debug(f"ASCOMSwitch.MinSwitchValue({ID}) called")
        return self._device.MinSwitchValue(ID)

    def SetSwitch(self, ID, State):
        logger.debug(f"ASCOMSwitch.SetSwitch({ID}, {State}) called")
        self._device.SetSwitch(ID, State)

    def SetSwitchName(self, ID, Name):
        logger.debug(f"ASCOMSwitch.SetSwitchName({ID}, {Name}) called")
        self._device.SetSwitchName(ID, Name)

    def SetSwitchValue(self, ID, Value):
        logger.debug(f"ASCOMSwitch.SetSwitchValue({ID}, {Value}) called")
        self._device.SetSwitchValue(ID, Value)

    def SwitchStep(self, ID):
        logger.debug(f"ASCOMSwitch.SwitchStep({ID}) called")
        self._device.SwitchStep(ID)

    @property
    def MaxSwitch(self):
        logger.debug("ASCOMSwitch.MaxSwitch property called")
        return self._device.MaxSwitch
