import logging
import platform

from .device import Device
from .observatory_exception import ObservatoryException

logger = logging.getLogger(__name__)


class ASCOMDevice(Device):
    def __init__(self, identifier, alpaca=False, device_type="Device", **kwargs):
        """
        Represents a generic ASCOM device.

        Provides a common interface to interact with ASCOM-compatible devices.
        Supports both Alpaca and COM-based ASCOM devices, allowing for cross-platform compatibility.

        Parameters
        ----------
        identifier : `str`
            The unique identifier for the ASCOM device. This can be the ProgID for COM devices or the device number for Alpaca devices.
        alpaca : `bool`, default : `False`, optional
            Whether the device is an Alpaca device and should use the appropriate communication protocol.
        device_type : `str`, default : "Device", optional
            The type of the ASCOM device (e.g. "Telescope", "Camera", etc.)
        **kwargs : `dict`, optional
            Additional keyword arguments to pass to the device constructor.
        """
        logger.debug(f"ASCOMDevice.__init__({identifier}, alpaca={alpaca}, {kwargs})")
        self._identifier = identifier
        self._device = None

        if alpaca:
            import alpaca

            self._device = getattr(
                getattr(
                    __import__("alpaca." + device_type.lower()), device_type.lower()
                ),
                device_type,
            )(self._identifier, **kwargs)
        elif platform.system() == "Windows":
            from win32com.client import Dispatch

            self._device = Dispatch(self._identifier)
        else:
            raise ObservatoryException("If you are not on Windows, you must use Alpaca")

    def Action(self, ActionName, *ActionParameters):  # pragma: no cover
        """
        Invokes the device-specific custom action on the device.

        Parameters
        ----------
        ActionName : `str`
            The name of the action to invoke. Action names are either specified by the device driver or are well known names agreed upon and constructed by interested parties.
        ActionParameters : `list`
            The required parameters for the given action. Empty string if none are required.
        
        Returns
        -------
        `str`
            The result of the action. The return value is dependent on the action being invoked and the representations are set by the driver author.
        
        Notes
        -----
        See `SupportedActions` for a list of supported actions set up by the driver author.
        Action names are case-insensitive, so be aware when creating new actions.
        """
        logger.debug(f"ASCOMDevice.Action({ActionName}, {ActionParameters})")
        return self._device.Action(ActionName, *ActionParameters)

    def CommandBlind(self, Command, Raw):  # pragma: no cover
        """
        Sends a command to the device and does not wait for a response.

        .. deprecated:: 0.1.1
            ASCOM is deprecating this method.

        Parameters
        ----------
        Command : `str`
            The command string to send to the device.
        Raw : `bool`
            If `True`, the command is set as-is. If `False`, protocol framing characters may be added onto the command.
        """

        logger.debug(f"ASCOMDevice.CommandBlind({Command}, {Raw})")
        self._device.CommandBlind(Command, Raw)

    def CommandBool(self, Command, Raw):  # pragma: no cover
        """
        Sends a command to the device and waits for a boolean response.

        .. deprecated:: 0.1.1
            ASCOM is deprecating this method.

        Parameters
        ----------
        Command : `str`
            The command string to send to the device.
        Raw : `bool`
            If `True`, the command is set as-is. If `False`, protocol framing characters may be added onto the command.
        
        Returns
        -------
        `bool`
            The boolean response from the device.
        """

        logger.debug(f"ASCOMDevice.CommandBool({Command}, {Raw})")
        return self._device.CommandBool(Command, Raw)

    def CommandString(self, Command, Raw):  # pragma: no cover
        """
        Sends a command to the device and waits for a string response.

        .. deprecated:: 0.1.1
            ASCOM is deprecating this method.

        Parameters
        ----------
        Command : `str`
            The command string to send to the device.
        Raw : `bool`
            If `True`, the command is set as-is. If `False`, protocol framing characters may be added onto the command.
        
        Returns
        -------
        `str`
            The string response from the device.
        """

        logger.debug(f"ASCOMDevice.CommandString({Command}, {Raw})")
        return self._device.CommandString(Command, Raw)

    @property
    def Connected(self):
        logger.debug(f"ASCOMDevice.Connected property")
        return self._device.Connected

    @Connected.setter
    def Connected(self, value):
        logger.debug(f"ASCOMDevice.Connected property set to {value}")
        self._device.Connected = value

    @property
    def Description(self):
        """
        The description of the device such as the manufacturer and model number. (`str`)
        
        Description should be limited to 64 characters so that it can be used in FITS headers.
        """
        logger.debug(f"ASCOMDevice.Description property")
        return self._device.Description

    @property
    def DriverInfo(self):
        """
        Description and version information about this ASCOM driver. (`str`)
        
        Length of info can contain line endings and may be up to thousands of characters long.
        Version data and copyright data should be included.
        See `Description` for information on the device itself.
        To get the version number in a parseable string, use `DriverVersion`.
        """
        logger.debug(f"ASCOMDevice.DriverInfo property")
        return self._device.DriverInfo

    @property
    def DriverVersion(self):
        """
        The driver version number, containing only the major and minor version numbers. (`str`)

        The format is "n.n" where "n" is a number.
        Not to be confused with `InterfaceVersion`, which is the version of the specification supported by the driver.
        """
        logger.debug(f"ASCOMDevice.DriverVersion property")
        return self._device.DriverVersion

    @property
    def InterfaceVersion(self):
        """Interface version number that this device supports. (`int`)"""
        logger.debug(f"ASCOMDevice.InterfaceVersion property")
        return self._device.InterfaceVersion

    @property
    def Name(self):
        logger.debug(f"ASCOMDevice.Name property")
        return self._device.Name

    @property
    def SupportedActions(self):
        """List of custom action names supported by this driver. (`list`)"""
        logger.debug(f"ASCOMDevice.SupportedActions property")
        return self._device.SupportedActions
