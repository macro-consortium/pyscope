import logging
import urllib.request

from ..utils import _get_number_from_line
from .safety_monitor import SafetyMonitor

logger = logging.getLogger(__name__)


class HTMLSafetyMonitor(SafetyMonitor):
    def __init__(self, url, check_phrase=b"ROOFPOSITION=OPEN"):
        """
        HTML implementation of the SafetyMonitor base class.

        This class provides an interface to access safety monitors,
        doing so using data fetched from a URL. This allows the observatory
        to check if weather, power, and other observatory-specific conditions
        allow safe usage of observatory equipment, such as opening the roof or dome.
        Other than the method `IsSafe`, this class also provides the properties
        for information about the driver, about the interface, description, and name.

        Parameters
        ----------
        url : `str`
            The URL to fetch data from.
        check_phrase : `bytes`, default : b"ROOFPOSITION=OPEN", optional
            The phrase to check for in the data fetched from the URL.
            In the default case, we would check if it is safe to open the roof.
        """
        logger.debug(
            f"""HTMLSafetyMonitor.__init__(
            {url}, check_phrase={check_phrase}) called"""
        )

        self._url = url
        self._check_phrase = check_phrase

    @property
    def IsSafe(self):
        """
        Whether the observatory equipment/action specified in the constructor's `check_phrase` is safe to use. (`bool`)
        """
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

    @property
    def DriverVersion(self):
        """Version of the driver. (`str`)"""
        logger.debug(f"""HTMLSafetyMonitor.DriverVersion property called""")
        return "1.0"

    @property
    def DriverInfo(self):
        """Information about the driver. (`str`)"""
        logger.debug(f"""HTMLSafetyMonitor.DriverInfo property called""")
        return "HTML Safety Monitor"

    @property
    def InterfaceVersion(self):
        """Version of the interface. (`str`)"""
        logger.debug(f"""HTMLSafetyMonitor.InterfaceVersion property called""")
        return "1.0"

    @property
    def Description(self):
        """Description of the driver. (`str`)"""
        logger.debug(f"""HTMLSafetyMonitor.Description property called""")
        return "HTML Safety Monitor"

    @property
    def SupportedActions(self):
        """List of supported actions. (`list`)"""
        logger.debug(f"""HTMLSafetyMonitor.SupportedActions property called""")
        return []

    @property
    def Name(self):
        """Name of the driver/url. (`str`)"""
        logger.debug(f"""HTMLSafetyMonitor.Name property called""")
        return self._url
