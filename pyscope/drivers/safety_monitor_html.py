import pycurl
import io
from . import abstract

class SafetyMonitorHTML(abstract.SafetyMonitor):
    def __init__(self, url, check_phrase=b'ROOFPOSITION=OPEN'):

        self._url = url
        self._check_phrase = check_phrase

    @property
    def IsSafe(self):
        safe = False
        buffer = io.BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self._url)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        if body.find(self._check_phrase) > -1:
            safe = True

        return(safe)