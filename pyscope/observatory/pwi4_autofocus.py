import logging
import time

from ._pwi4 import _PWI4
from .autofocus import Autofocus

logger = logging.getLogger(__name__)


class PWI4Autofocus(Autofocus):
    def __init__(self, host="localhost", port=8220):
        self._host = host
        self._port = port
        self._app = _PWI4(host=self._host, port=self._port)

    def Run(self, *args, **kwargs):
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
        logger.debug("Aborting autofocus in PWI4Autofocus")
        _ = self._app.focuser_stop()
