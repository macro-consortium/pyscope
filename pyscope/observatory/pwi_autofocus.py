import logging
import platform
import time

from .autofocus import Autofocus

logger = logging.getLogger(__name__)


class PWIAutofocus(Autofocus):
    def __init__(self):
        """
        Autofocus class for PlaneWave Instruments focuser.

        This class provides an interface for autofocus running, and aborting on the PlaneWave Instruments focuser.
        """
        logger.debug("PWIAutofocus.__init__ called")
        if platform.system() != "Windows":
            raise Exception("This class is only available on Windows.")
        else:
            from win32com.client import Dispatch

            self._com_object = Dispatch("PlaneWave.AutoFocus")

            self._com_object.StartPwiIfNeeded
            self._forward_autofocus_messages()
            self._com_object.ConnectFocuser
            self._forward_autofocus_messages()

            # Wait up to 3 seconds for a confirmed connection
            t = time.time() + 3
            while not self._com_object.IsFocuserConnected:
                if time.time() > t:
                    raise Exception("Unable to connect to focuser.")
                time.sleep(0.1)
                self._forward_autofocus_messages()

            self._com_object.PreventFilterChange = True

    def Run(self, exposure=10, timeout=120):
        """
        Run the autofocus routine on the PlaneWave Instruments focuser.
        Only returns once the autofocus routine has completed.

        Parameters
        ----------
        exposure : `float`, default : 10, optional
            Exposure time in seconds for the autofocus routine.
        timeout : `float`, default : 120, optional
            Timeout in seconds for the autofocus routine to complete.

        Returns
        -------
        `float` or `None`
            The best position found by the autofocus routine, or None if the autofocus routine failed.
        """
        logger.debug(
            f"PWIAutofocus.Run called with args: exposure={exposure}, timeout={timeout}"
        )
        self._com_object.ExposureLengthSeconds = exposure

        if not self._com_object.IsFocuserConnected:
            raise Exception(
                "Unable to run PlaneWave AutoFocus: focuser is not connected"
            )

        self._com_object.StartAutoFocus

        t = time.time() + timeout
        while self._com_object.IsAutoFocusRunning:
            self._forward_autofocus_messages()
            time.sleep(0.2)

            if time.time() > t:
                raise Exception(
                    "Autofocus took longer than %g seconds to complete" % timeout
                )

        if self._com_object.Success:
            return self._com_object.BestPosition
        else:
            return None

    def Abort(self):
        """
        Abort the autofocus routine on the PlaneWave Instruments focuser.
        """
        logger.debug("PWIAutofocus.Abort called")
        self._com_object.StopAutofocus

    def _forward_autofocus_messages(self):
        while True:
            log_line = self._com_object.NextLogMessage
            if log_line is None:
                return
            logger.info(log_line)
