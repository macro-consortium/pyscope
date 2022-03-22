import time

import ephem

class MySun(ephem._libastro.Planet):
    __planet__ = 8


site = ephem.Observer()
site.lat = "-30:00:00"
site.lon = "-110:00:00"

sun = MySun()

while True:
    site.date = ephem.now()    
    sun.compute(site)
    print(sun.ra, sun.dec, sun.alt, sun.az)

    time.sleep(1)