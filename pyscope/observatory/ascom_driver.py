import platform

if platform.system() == 'Windows':
    from win32com.client import Dispatch

from .driver import Driver

class ASCOMDriver(Driver):
    def __init__(self, com_object_name):
        self._com_object_name = com_object_name
        self._com_object = Dispatch(self._com_object_name)

    def Action(self, ActionName, ActionParameters):
        self._com_object.Action(ActionName, ActionParameters)

    def CommandBlind(self, Command, Raw):
        self._com_object.CommandBlind(Command, Raw)

    def CommandBool(self, Command, Raw):
        self._com_object.CommandBool(Command, Raw)

    def CommandString(self, Command, Raw):
        self._com_object.CommandString(Command, Raw)

    def Dispose(self):
        self._com_object.Dispose()

    def SetupDialog(self):
        self._com_object.SetupDialog()

    @property
    def Connected(self):
        return self._com_object.Connected
    @Connected.setter
    def Connected(self, value):
        self._com_object.Connected = value
    
    @property
    def Description(self):
        return self._com_object.Description
    
    @property
    def DriverInfo(self):
        return self._com_object.DriverInfo
    
    @property
    def DriverVersion(self):
        return self._com_object.DriverVersion
    
    @property
    def InterfaceVersion(self):
        return self._com_object.InterfaceVersion

    @property
    def Name(self):
        return self._com_object.Name
    
    @property
    def SupportedActions(self):
        return self._com_object.SupportedActions