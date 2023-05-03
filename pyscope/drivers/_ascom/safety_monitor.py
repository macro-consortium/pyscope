from .driver import Driver
from .. import abstract

class SafetyMonitor(Driver, abstract.SafetyMonitor):
    def Choose(self, SafetyMonitorID):
        self._com_object.Choose(SafetyMonitorID)
    
    @property
    def IsSafe(self):
        return self._com_object.IsSafe