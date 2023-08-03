from .safety_monitor import SafetyMonitor

class ASCOMSafetyMonitor(SafetyMonitor):
    def Choose(self, SafetyMonitorID):
        self._com_object.Choose(SafetyMonitorID)
    
    @property
    def IsSafe(self):
        return self._com_object.IsSafe