import logging
import urllib.request

from ..utils import _get_number_from_line
from .safety_monitor import SafetyMonitor

logger = logging.getLogger(__name__)


class HTMLSafetyMonitor(SafetyMonitor):
    def __init__(self, url, check_phrase=b"ROOFPOSITION=OPEN"):
        logger.debug(
            f"""HTMLSafetyMonitor.__init__(
            {url}, check_phrase={check_phrase}) called"""
        )

        self._url = url
        self._check_phrase = check_phrase

    @property
    def IsSafe(self):
        logger.debug(f"""HTMLSafetyMonitor.IsSafe property called""")
        safe = None

        stream = urllib.request.urlopen(self._url)
        lines = stream.readlines()

        try:
            units = self._check_phrase.split(b" ")[1]
        except IndexError:
            units = ""

        for line in lines:
            s = _get_number_from_line(
                line,
                self._check_phrase.split(b"=")[0],
                units,
                False,
            )
            if s == self._check_phrase.split(b"=")[1]:
                safe = True
                break
        else:
            safe = False

        return safe
