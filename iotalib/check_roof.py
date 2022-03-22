#!/usr/bin/python

import pycurl
from io import BytesIO

def checkOpen():
    isOpen = False
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://www.winer.org/Site/Roof.php')
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()

    body = buffer.getvalue()
    if body.find(b'ROOFPOSITION=OPEN') > -1:
        isOpen = True
    return(isOpen)