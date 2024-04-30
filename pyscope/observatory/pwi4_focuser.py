import logging
import time

from ._pwi4 import _PWI4
from .focuser import Focuser

logger = logging.getLogger(__name__)


class PWI4Focuser(Focuser):
    def __init__(self, host="localhost", port=8220):
        self._host = host
        self._port = port
        self._app = _PWI4(host=self._host, port=self._port)

    def Enabled(self):
        logger.debug("Checking if focuser is enabled in PWI4Focuser")
        self._app.request("/autofocus/start")
        return True

    def Halt(self, return_status=False):
        logger.debug("PWI4Focuser.Halt(return_status={}) called".format(return_status))
        if return_status:
            return self._app.focuser_stop()
        else:
            _ = self._app.focuser_stop()

    def Move(self, Position, return_status=False):
        logger.debug(
            "PWI4Focuser.Move(Position={}, return_status={}) called".format(
                Position, return_status
            )
        )
        if return_status:
            return self._app.focuser_goto(target=Position)
        else:
            _ = self._app.focuser_goto(target=Position)

    @property
    def Absolute(self):
        return True

    @Absolute.setter
    def Absolute(self, value):
        raise NotImplementedError

    @property
    def Description(self):
        return "PWI4 Focuser"

    @property
    def DriverInfo(self):
        return "PWI4Driver"

    @property
    def DriverVersion(self):
        return "PWI4Driver"

    @property
    def InterfaceVersion(self):
        return "PWI4Interface"

    @property
    def IsMoving(self):
        logger.debug("PWI4Focuser.IsMoving() called")
        return self._app.status().focuser.is_moving

    @property
    def MaxIncrement(self):
        raise NotImplementedError

    @property
    def MaxStep(self):
        raise NotImplementedError

    @property
    def Name(self):
        return "PWI4 Focuser"

    @property
    def Position(self):
        logger.debug("PWI4Focuser.Position() called")
        return self._app.status().focuser.position

    @property
    def StepSize(self):
        raise NotImplementedError

    @property
    def TempComp(self):
        raise NotImplementedError

    @TempComp.setter
    def TempComp(self, value):
        raise NotImplementedError

    @property
    def TempCompAvailable(self):
        return False

    @property
    def Temperature(self):
        raise NotImplementedError

    @Temperature.setter
    def Temperature(self, value):
        raise NotImplementedError

    @property
    def Connected(self):
        logger.debug("PWI4Focuser.Connected() called")
        if self._app.status().focuser.exists:
            return (
                self._app.status().focuser.is_connected
                and self._app.status().focuser.is_enabled
            )
        else:
            return False

    @property
    def Enabled(self):
        logger.debug("PWI4Focuser.Enabled() called")
        return self._app.status().focuser.is_enabled

    @Connected.setter
    def Connected(self, value):
        logger.debug("PWI4Focuser.Connected(value={}) called".format(value))
        if value:
            _ = self._app.focuser_connect()
            _ = self._app.focuser_enable()
        else:
            _ = self._app.focuser_disconnect()
            _ = self._app.focuser_disable()
