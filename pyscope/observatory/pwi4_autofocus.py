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

    def Run(self):
        logger.debug("Starting autofocus in PWI4Autofocus")
        self._app.request("/autofocus/start")
        logger.info("Autofocus started, sleeping for 210 seconds")
        time.sleep(210)
        logger.info("Autofocus complete")
        return True
    
    def Abort(self):
        logger.debug("Aborting autofocus in PWI4Autofocus")
        _ = self._app.focuser_stop()

