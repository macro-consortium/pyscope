import logging
import time
import dlipower

from .switch import Switch

logger = logging.getLogger(__name__)

class DLIPowerSwitch(Switch):
    def __init__(self, name, hostname, userid, password):
        """
        Initialize the DLIPowerSwitch instance.
        :param hostname: Hostname or IP address of the DLI power switch.
        :param userid: Username for authentication.
        :param password: Password for authentication.
        """
        self.hostname = hostname
        self.userid = userid
        self.password = password
        self.name = name
        try:
            self.switch = dlipower.PowerSwitch(hostname=self.hostname, userid=self.userid, password=self.password)
        except Exception as e:
            logger.error("Failed to connect to DLIPowerSwitch: %s", e)
            raise

    def CanWrite(self, ID):
        return True  # All outlets are writable in DLIPower

    def GetSwitch(self, ID):
        return self.switch[int(ID) - 1].state.lower() == 'on'

    def GetSwitchDescription(self, ID):
        return self.switch[int(ID) - 1].description

    def GetSwitchName(self, ID):
        return self.switch[int(ID) - 1].name

    def MaxSwitchValue(self, ID):
        return 1  # Binary switch: ON is 1

    def MinSwitchValue(self, ID):
        return 0  # Binary switch: OFF is 0

    def SetSwitch(self, ID, State):
        outlet = self.switch[int(ID) - 1]
        try:
            outlet.state = 'ON' if State else 'OFF'
        except Exception as e:
            logger.error("Failed to set switch %s to %s: %s", ID, 'ON' if State else 'OFF', e)
            raise

    def SetSwitchName(self, ID, Name):
        try:
            self.switch[int(ID) - 1].name = Name
        except Exception as e:
            logger.error("Failed to set name for switch %s: %s", ID, e)
            raise

    def SetSwitchValue(self, ID, Value):
        self.SetSwitch(ID, bool(Value))

    def SwitchStep(self, ID):
        return 1  # Binary switches step in increments of 1 (ON/OFF)

    def RebootSwitch(self, ID):
        outlet = self.switch[int(ID) - 1]
        try:
            outlet.cycle()
        except Exception as e:
            logger.error("Failed to reboot switch %s: %s", ID, e)
            raise

    def ToggleSwitch(self, ID):
        current_state = self.GetSwitch(ID)
        self.SetSwitch(ID, not current_state)

    def AllOn(self):
        try:
            for outlet in self.switch:
                outlet.state = 'ON'
        except Exception as e:
            logger.error("Failed to turn all switches ON: %s", e)
            raise

    def AllOff(self):
        try:
            for outlet in self.switch:
                outlet.state = 'OFF'
        except Exception as e:
            logger.error("Failed to turn all switches OFF: %s", e)
            raise

    def PowerCycleAll(self):
        try:
            for outlet in self.switch:
                if outlet.state == 'ON':
                    outlet.state = 'OFF'
                    time.sleep(10)
                    outlet.state = 'ON'
                else:
                    pass
        except Exception as e:
            logger.error("Failed to power cycle all switches: %s", e)
            raise

    def Status(self):
        try:
            return {outlet.name: outlet.state for outlet in self.switch}
        except Exception as e:
            logger.error("Failed to retrieve status of all switches: %s", e)
            raise

    @property
    def MaxSwitch(self):
        return len(self.switch)

    @property
    def Name(self):
        return self.name
    
    @property
    def Hostname(self):
        return self.hostname
    
    