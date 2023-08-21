import logging

from .switch import Switch

logger = logging.getLogger(__name__)


class ASCOMSwitch(Switch):
    def CanWrite(self, ID):
        logger.debug(f"ASCOMSwitch.CanWrite({ID}) called")
        return self._com_object.CanWrite(ID)

    def Choose(self, SwitchID):
        logger.debug(f"ASCOMSwitch.Choose({SwitchID}) called")
        self._com_object.Choose(SwitchID)

    def GetSwitch(self, ID):
        logger.debug(f"ASCOMSwitch.GetSwitch({ID}) called")
        return self._com_object.GetSwitch(ID)

    def GetSwitchDescription(self, ID):
        logger.debug(f"ASCOMSwitch.GetSwitchDescription({ID}) called")
        return self._com_object.GetSwitchDescription(ID)

    def GetSwitchName(self, ID):
        logger.debug(f"ASCOMSwitch.GetSwitchName({ID}) called")
        return self._com_object.GetSwitchName(ID)

    def MaxSwitchValue(self, ID):
        logger.debug(f"ASCOMSwitch.MaxSwitchValue({ID}) called")
        return self._com_object.MaxSwitchValue(ID)

    def MinSwitchValue(self, ID):
        logger.debug(f"ASCOMSwitch.MinSwitchValue({ID}) called")
        return self._com_object.MinSwitchValue(ID)

    def SetSwitch(self, ID, State):
        logger.debug(f"ASCOMSwitch.SetSwitch({ID}, {State}) called")
        self._com_object.SetSwitch(ID, State)

    def SetSwitchName(self, ID, Name):
        logger.debug(f"ASCOMSwitch.SetSwitchName({ID}, {Name}) called")
        self._com_object.SetSwitchName(ID, Name)

    def SetSwitchValue(self, ID, Value):
        logger.debug(f"ASCOMSwitch.SetSwitchValue({ID}, {Value}) called")
        self._com_object.SetSwitchValue(ID, Value)

    def SwitchStep(self, ID):
        logger.debug(f"ASCOMSwitch.SwitchStep({ID}) called")
        self._com_object.SwitchStep(ID)

    @property
    def MaxSwitch(self):
        logger.debug("ASCOMSwitch.MaxSwitch property called")
        return self._com_object.MaxSwitch
