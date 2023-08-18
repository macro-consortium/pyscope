# import pycurl
# import io

from .safety_monitor import SafetyMonitor

class HTMLSafetyMonitor(SafetyMonitor):
    def __init__(self, url, check_phrase=b'ROOFPOSITION=OPEN'):
        logger.debug(f'''HTMLSafetyMonitor.__init__(
            {url}, check_phrase={check_phrase}) called''')

        self._url = url
        self._check_phrase = check_phrase

    @property
    def IsSafe(self):
        logger.debug(f'''HTMLSafetyMonitor.IsSafe property called''')
        safe = False
        c = None
        # buffer = io.BytesIO()
        # c = pycurl.Curl()
        c.setopt(c.URL, self._url)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        if body.find(self._check_phrase) > -1:
            safe = True

        return(safe)