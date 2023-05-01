from . import Driver
from .. import abstract

class Switch(Driver, abstract.Switch):
    def CanWrite(self, ID):
        return self._com_object.CanWrite(ID)

    def Choose(self, SwitchID):
        self._com_object.Choose(SwitchID)
    
    def GetSwitch(self, ID):
        return self._com_object.GetSwitch(ID)
    
    def GetSwitchDescription(self, ID):
        return self._com_object.GetSwitchDescription(ID)

    def GetSwitchName(self, ID):
        return self._com_object.GetSwitchName(ID)
    
    def MaxSwitchValue(self, ID):
        return self._com_object.MaxSwitchValue(ID)

    def MinSwitchValue(self, ID):
        return self._com_object.MinSwitchValue(ID)
    
    def SetSwitch(self, ID, State):
        self._com_object.SetSwitch(ID, State)

    def SetSwitchName(self, ID, Name):
        self._com_object.SetSwitchName(ID, Name)
        
    def SetSwitchValue(self, ID, Value):
        self._com_object.SetSwitchValue(ID, Value)
    
    def SwitchStep(self, ID):
        self._com_object.SwitchStep(ID)
    
    @property
    def MaxSwitch(self):
        return self._com_object.MaxSwitch