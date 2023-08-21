import logging
from .safety_monitor import SafetyMonitor

logger = logging.getLogger(__name__)


class ASCOMSafetyMonitor(SafetyMonitor):
    def Choose(self, SafetyMonitorID):
        logger.debug(f"ASCOMSafetyMonitor.Choose({SafetyMonitorID}) called")
        self._com_object.Choose(SafetyMonitorID)

    @property
    def IsSafe(self):
        logger.debug(f"ASCOMSafetyMonitor.IsSafe property called")
        return self._com_object.IsSafe
