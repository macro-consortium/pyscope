import ephem as ep  # pyephem library
import re
import urllib.request, urllib.parse, urllib.error
from math import *


class SesameError(Exception):
    pass


class NameNotFoundError(Exception):
    pass


class ObjectFinder():

    def sesame_resolve(self, name):  # This handy function from KMI
        url = "http://vizier.u-strasbg.fr/viz-bin/nph-sesame/-oI/SNV?"
        object = urllib.parse.quote(name)
        ra = None
        dec = None
        identifiers = []
        try:
            simbad_lines = urllib.request.urlopen(url + object).readlines()
        except Exception as e:
            raise SesameError("Unable to connect to Sesame server", e)
        for line in simbad_lines:
            line = line.strip()
            if line.startswith("%J "):
                fields = re.split(r" +", line)
                try:
                    # raises ValueError, IndexError
                    ra = float(fields[1]) / 15.0
                    dec = float(fields[2])  # raises ValueError, IndexError
                except (ValueError, IndexError) as e:
                    raise SesameError("Error parsing Sesame response", e)
            if line.startswith("%I "):
                fields = line.split(" ", 1)
                try:
                    identifiers.append(fields[1])  # raises IndexError
                except IndexError as e:
                    raise SesameError("Error parsing Sesame response", e)
        if (ra is None or dec is None):
            raise NameNotFoundError("Name not found by Sesame server")
        return (ra, dec, identifiers)

    def hr2hms(self, rahr):
        rahms = str(ep.hours(rahr * pi / 12))
        return rahms

    def deg2dms(self, decdeg):
        decdms = str(ep.degrees(decdeg * pi / 180.))
        return decdms

    def get_times(self, t):
        winer.date = t
        local = str(ep.Date(winer.date - 7 * ep.hour)).split()[1][0:8]
        ut = str(t).split()[1][0:8]
        lst = str(winer.sidereal_time()).split()[0][0:8]
        return local, ut, lst
