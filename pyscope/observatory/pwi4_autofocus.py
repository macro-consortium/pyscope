import logging
import time

from ._pwi4 import _PWI4
from .autofocus import Autofocus

logger = logging.getLogger(__name__)


class PWI4Autofocus(Autofocus):
    def __init__(self, host="localhost", port=8220):
        """
        Autofocus class for the PlaneWave Interface 4 (PWI4) utility platform.

        This class provides an interface for autofocus running, and aborting on the PWI4 platform.

        Parameters
        ----------
        host : `str`, default : "localhost", optional
            The host of the PWI4 server.
        port : `int`, default : 8220, optional
            The port of the PWI4 server.
        """
        self._host = host
        self._port = port
        self._app = _PWI4(host=self._host, port=self._port)

    def Run(self, *args, **kwargs):
        """
        Run the autofocus routine on the PWI4 platform.
        Only returns once the autofocus routine is complete.

        Parameters
        ----------
        *args : `tuple`
            Variable length argument list.
        **kwargs : `dict`
            Arbitrary keyword arguments.
        
        Returns
        -------
        `float`
            The best focuser position found by the autofocus routine.
        """
        logger.debug("Starting autofocus in PWI4Autofocus")
        self._app.request("/autofocus/start")
        logger.info("Autofocus started")
        time.sleep(1)
        while self._app.status().autofocus.is_running:
            time.sleep(1)
        logger.info("Autofocus complete")

        logger.info("Moving focuser to best position")
        while self._app.status().focuser.is_moving:
            time.sleep(1)
        logger.info("Focuser moved to best position")

        return self._app.status().autofocus.best_position

    def Abort(self):
        """
        Abort the autofocus routine on the PWI4 platform.
        """
        logger.debug("Aborting autofocus in PWI4Autofocus")
        _ = self._app.focuser_stop()
