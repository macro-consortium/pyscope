import pycurl
import io
from . import abstract

class SafetyMonitorHTML(abstract.SafetyMonitor):
    def __init__(self, *args, **kwargs):

        self.url = args[0] if len(args) > 0 else kwargs['url']
        self._check_phrase = kwargs['check_phrase'] if 'check_phrase' in kwargs else b'ROOFPOSITION=OPEN'

    @property
    def IsSafe(self):
        safe = False
        buffer = io.BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.url)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        if body.find(self._check_phrase) > -1:
            safe = True

        return(safe)