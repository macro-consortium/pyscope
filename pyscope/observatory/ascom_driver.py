import platform
import logging

logger = logging.getLogger(__name__)

if platform.system() == 'Windows':
    from win32com.client import Dispatch
else:
    logger.warning('ASCOM drivers are only supported on Windows, import allowed for testing purposes only')

class ASCOMDriver(Driver):
    def __init__(self, com_object_name):
        logger.debug(f"ASCOMDriver.__init__({com_object_name}) called")
        self._com_object_name = com_object_name
        self._com_object = None
        if platform.system() == 'Windows':
            from win32com.client import Dispatch
            self._com_object = Dispatch(self._com_object_name)

    def Action(self, ActionName, ActionParameters):
        logger.debug(f"ASCOMDriver.Action({ActionName}, {ActionParameters}) called")
        self._com_object.Action(ActionName, ActionParameters)

    def CommandBlind(self, Command, Raw):
        logger.debug(f"ASCOMDriver.CommandBlind({Command}, {Raw}) called")
        self._com_object.CommandBlind(Command, Raw)

    def CommandBool(self, Command, Raw):
        logger.debug(f"ASCOMDriver.CommandBool({Command}, {Raw}) called")
        self._com_object.CommandBool(Command, Raw)

    def CommandString(self, Command, Raw):
        logger.debug(f"ASCOMDriver.CommandString({Command}, {Raw}) called")
        self._com_object.CommandString(Command, Raw)

    def Dispose(self):
        logger.debug(f"ASCOMDriver.Dispose() called")
        self._com_object.Dispose()

    def SetupDialog(self):
        logger.debug(f"ASCOMDriver.SetupDialog() called")
        self._com_object.SetupDialog()

    @property
    def Connected(self):
        logger.debug(f"ASCOMDriver.Connected property called")
        return self._com_object.Connected
    @Connected.setter
    def Connected(self, value):
        logger.debug(f"ASCOMDriver.Connected property set to {value}")
        self._com_object.Connected = value
    
    @property
    def Description(self):
        logger.debug(f"ASCOMDriver.Description property called")
        return self._com_object.Description
    
    @property
    def DriverInfo(self):
        logger.debug(f"ASCOMDriver.DriverInfo property called")
        return self._com_object.DriverInfo
    
    @property
    def DriverVersion(self):
        logger.debug(f"ASCOMDriver.DriverVersion property called")
        return self._com_object.DriverVersion
    
    @property
    def InterfaceVersion(self):
        logger.debug(f"ASCOMDriver.InterfaceVersion property called")
        return self._com_object.InterfaceVersion

    @property
    def Name(self):
        logger.debug(f"ASCOMDriver.Name property called")
        return self._com_object.Name
    
    @property
    def SupportedActions(self):
        logger.debug(f"ASCOMDriver.SupportedActions property called")
        return self._com_object.SupportedActions