"""
Routines for parsing telrun.sls files
"""

import logging
import math
import os
import re

import ephem

from . import convert

logger = logging.getLogger(__name__)

##### Various enum constants used in telrun scan structures #####

# CCDShutterOptions values (from libmisc/ccdcamera.h)
CCDSO_CLOSED = "Closed"
CCDSO_OPEN = "Open"
CCDSO_DBL = "Dbl Expose"
CCDSO_MULTI = "Multi Expose"

# CCType values (from libmisc/scan.h)
CT_NONE = 0  # Take no new cal files
CT_BIAS = 1  # Take fresh bias
CT_THERMAL = 2 # Take fresh bias + thermal
CT_FLAT = 3    # Take fresh bias + thermal + flat
CT_FOCUSPOS = 4 # Set focus to an absolute position, in microns
CT_FOCUSOFF = 5 # Offset focus position +/- amount of microns from current position. Offset stored in ra_offset
CT_AUTOFOCUS = 6 # Perform autofocus. Position stored in ra_offset
CT_FIXEDALTAZ = 7 # Slew telescope to ra_offset,dec_offset and take exposure without tracking
CT_EXTCMD = 8 # Another extended action; keyword CMDLINE; comment-enabled SCH transfers, etc.

# CCData values (from libmisc.scan.h)
CD_NONE = 0   # Take no new "data", just possibly cal files
CD_RAW = 1    # Take data but do not calibrate
CD_COOKED = 2 # Take data and calibrate

##### Other (non-enum) constants used in telrun scan code #####

# Various constants 

# from libmisc/scan.c:
COMMENT1 = '!' # Beginning of a comment
COMMENT2 = '#' # Another legal beginning of a comment
FIRSTCOL = 22  # First column to use in a line (0-based)
LASTLINE = 21  # Last line number in a scan (0-based)

# from libmisc/scan.h:
NO_ALTAZ_ENTRY = -99

# from libastro/astro.h:
SPD = 24.0*3600.0   # Seconds per day
MJD0 = 2415020.0    # Starting point for MJD calculations

# Status line values
STATUS_NEW = "N"   # Scan has not yet been performed
STATUS_DONE = "D"  # Scan has been performed
STATUS_FAIL = "F"  # Scan failed to be performed


##### Structures replated to telrun scans #####

class CCDCalib(object):
    """
    The CCDCalib struct, from libmisc/scan.h
    """

    def __init__(self):
        self.newc = CT_NONE # Which new cal files to take, if any (one of the CT_* constants)
        self.data = CD_NONE # How to process new data, if any (one of the CD_* constants)

class TelrunScan(object):
    """
    Represent a single entry (called a "Scan" in Talon) in a telrun file.
    """

    def __init__(self):
        # Set up the fields found in a Scan.
        # Mirrors the layout of the Scan struct (from libmisc/scan.h)

        # file info
        self.schedfn = ""  # basename of original .sch schedule file
        self.imagefn = ""  # basename of image to create
        self.imagedn = ""  # directory of image to create

        # object definition
        self.comment = "" # COMMENT header
        self.title = ""    # TITLE header
        self.observer = "" # OBSERVER header
        self.obj = None    # definition of the target object, read from the DB line (an instance of ephem.Body)
        self.rao = 0        # additional ra offset, in rads
        self.deco = 0       # additional dec offset, in rads
        self.extcmd = ""    # open-ended extension hook that changes the ext. stuff more

        # camera settings
        self.ccdcalib = CCDCalib() # how/whether to calibrate + keyword extensions
        self.cmosmode = 3   # 0=HDR, 1=High, 2=Low, 3=Stackpro
        self.sx = 0         # SUBIMAGE leftmost column
        self.sy = 0         # SUBIMAGE topmost row
        self.sw = 0         # SUBIMAGE width
        self.sh = 0         # SUBIMAGE height
        self.binx = 1       # BINNING in x direction
        self.biny = 1       # BINNING in y direction
        self.posx = None      # X position of the window, -1 no WCS solution
        self.posy = None      # Y position of the window, -1 no WCS solution
        self.interrupt_allowed = True
        self.dur = 1.0      # DURATION, seconds
        self.shutter = CCDSO_OPEN # how to operate shutter during exposure (one of the CCDSO_* constants)
        self.filter = ''    # FILTER, first character only

        # run details
        self.priority = 0   # assign lower values first
        self.running = 0    # set when actually in progress
        self.starttm = 0    # if not 0, when current run began or next starts (in same units as time.time())
        self.startdt = 0    # allowed startm +/- tolerance, seconds
        self.status = STATUS_NEW   # .sls status code character: N(ew)/D(one)/F(ail)

        # Additional fields not included in the original telrun struct:

        # Position of this scan's Status byte in the original telrun file
        self.status_offset = None


    def __str__(self):
        """
        Convert scan to a printable string
        """

        result = ""
        result += "schedfn: %r\n" % self.schedfn
        result += "imagefn: %r\n" % self.imagefn
        result += "imagedn: %r\n" % self.imagedn
        result += "comment: %r\n" % self.comment
        result += "title: %r\n" % self.title
        result += "observer: %r\n" % self.observer
        result += "obj: %r\n" % self.obj
        result += "rao: %r\n" % self.rao
        result += "deco: %r\n" % self.deco
        result += "extcmd: %r\n" % self.extcmd
        result += "ccdcalib: %r\n" % self.ccdcalib
        result += "cmosmode: %r\n" % self.cmosmode
        result += "sx: %r\n" % self.sx
        result += "sy: %r\n" % self.sy
        result += "sw: %r\n" % self.sw
        result += "sh: %r\n" % self.sh
        result += "binx: %r\n" % self.binx
        result += "biny: %r\n" % self.biny
        result += "dur: %r\n" % self.dur
        result += "shutter: %r\n" % self.shutter
        result += "filter: %r\n" % self.filter
        result += "priority: %r\n" % self.priority
        result += "running: %r\n" % self.running
        result += "starttm: %r\n" % self.starttm
        result += "startdt: %r\n" % self.startdt
        result += "status: %r\n" % self.status
        result += "status_offset: %r\n" % self.status_offset

        return result

class TelrunFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.scans = []

        f = open(filename, "r", encoding='utf-8')

        while True:
            result, scan, offset = read_next_sls(f)
            if result == 0:
                scan.status_offset = offset
                self.scans.append(scan)
            elif result == -2:
                break
            else:
                logger.warn("Error parsing complete SLS file")
                break

        f.close()

        logger.info("Read %d scans from %s", len(self.scans), filename)

    def update_status_code(self, scan, code):
        scan.status = code
        f = open(self.filename, "r+")
        f.seek(scan.status_offset, 0)
        f.write(code[0])
        f.close()



def read_next_sls(file_stream):
    """
    Given an open file stream (e.g. the result of the open(fn) function),
    read the next SLS entry from the stream.

    Returns a tuple:
      (result, scan, offset)
    
    where:
      result = 0 if a scan is found, -1 if there was a problem, or -2 if we've reached the end of the file
      scan = an instance of TelrunScan, or None if there was a problem
      offset = the offset of the status byte, or 0 if there was a problem
    
    Based on readNextSLS() from talon/libmisc/scan.c
    """

    return_value_on_error = (-1, None, 0) # The tuple to return if there is a problem
    return_value_on_eof = (-2, None, 0) # The tuple to return when we reach the end of the file

    sp = None # The TelrunScan object that will be populated from the file (sp = Scan Pointer in old C code)
    offset = -1  # The byte offset into file_stream where the Status code (N/D/F) can be found

    lineno = 0 # The line we are on within the currrent Scan
    while lineno <= LASTLINE:
        line = file_stream.readline()
        if line == '':
            # End of file
            return return_value_on_eof

        # basic checks for comments and being in sync
        if line.startswith(COMMENT1) or line.startswith(COMMENT2):
            continue

        try:
            line_id_str = line[:2]      # Pull out leading digits (hopefully)
            line_id = int(line_id_str)  # Try to convert to an integer
            if line_id != lineno:
                logger.warn("Expected line ID number to be %d, but got %d; skipping to next line",
                    lineno,
                    line_id
                    )
                lineno = 0
                continue
        except:
            logger.warn("Unable to parse line ID '%s' as an integer; skipping to next scan", 
                    line_id_str)
            lineno = 0
            continue

        # strip off trailing newline (shouldn't need to worry about excessively long lines in Python)
        # keep track of how many characters we stripped off so that we can later get an
        # offset to the status code
        old_length = len(line)
        line = line.rstrip('\r\n') # remove any sequence of trailing character in the set ('\r', '\n')
        num_stripped_chars = old_length - len(line)


        # get the contents of the line, stripping off the line number and field description
        bp = line[FIRSTCOL:]

        # crack the field
        if lineno == 0:
            # Sample line:
            # 0            status: N
            if bp not in ['N', 'D', 'F']:
                logger.warn("Bad .sls status code: %s" % bp)
                lineno = 0
                continue

            sp = TelrunScan()
            sp.status = bp
            offset = file_stream.tell() - num_stripped_chars - 1 # back up over status code and newline

        elif lineno == 1:
            # Sample line:
            # 1          start JD: 2457137.62014 ( 4/25/2015  2:53 UTC)
            try:
                tmp = _atof(bp)
            except:
                logger.warn("Unable to parse '%s' as float; skipping to next scan", 
                        bp)
                lineno = 0
                continue

            # mjd was 25567.5 on 00:00:00 1/1/1970 UTC (UNIX epoch)
            sp.starttm = (tmp - MJD0 - 25567.5)*SPD + 0.5

        elif lineno == 2:
            # Sample line:
            # 2    lstdelta, mins: 9000  
            try:
                tmp = _atof(bp)
            except:
                logger.warn("Unable to parse '%s' as float; skipping to next scan", 
                        bp)
                lineno = 0
                continue
            sp.startdt = int(math.floor(tmp*60+0.5))

        elif lineno == 3:
            # Sample line:
            # 3           schedfn: gad97.sch
            sp.schedfn = bp

        elif lineno == 4:
            # Sample line:
            #  4             title: Jupiter Mass
            sp.title = bp

        elif lineno == 5:
            # Sample line:
            #  5          observer: nick-becker@uiowa.edu
            sp.observer = bp

        elif lineno == 6:
            # Sample line:
            #  6           comment: 
            sp.comment = bp

        elif lineno == 7:
            # Sample line:
            #  7               EDB: Jupiter,P
            try:
                sp.obj = edb_line_to_body(bp)
                sp.raw_edb = bp
            except Exception as ex:
                logger.warn("Unable to process target object '%s': '%s'; skipping to next scan",
                        bp,
                        ex.message)
                lineno = 0
                continue

        elif lineno == 8:
            # Sample line:
            #  8          RAOffset:  0:00:00.0
            try: 
                sp.rao = convert.hours_to_rads(convert.from_dms(bp))
            except:
                logger.warn("Unable to parse '%s' as sexagesimal string; skipping to next scan",
                        bp)
                lineno = 0
                continue

        elif lineno == 9:
            # Sample line:
            #  9         DecOffset:  0:00:00.0
            try: 
                sp.deco = convert.degs_to_rads(convert.from_dms(bp))
            except:
                logger.warn("Unable to parse '%s' as sexagesimal string; skipping to next scan",
                        bp)
                lineno = 0
                continue

        elif lineno == 10:
            # Sample line:
            # 10    frame position: 0+0
            try:
                sx_str, sy_str = bp.split("+")
                sp.sx = int(sx_str)
                sp.sy = int(sy_str)
            except Exception as ex:
                logger.warn("Invalid frame position '%s': %s; skipping to next scan",
                        bp,
                        ex.message)
                lineno = 0
                continue

        elif lineno == 11:
            # Sample line:
            # 11        frame size: 4096x4096
            try:
                sw_str, sh_str = bp.split("x")
                sp.sw = int(sw_str)
                sp.sh = int(sh_str)
            except Exception as ex:
                logger.warn("Invalid frame size '%s': %s; skipping to next scan",
                        bp,
                        ex.message)
                lineno = 0
                continue

        elif lineno == 12:
            # Sample line:
            # 12           binning: 2x2
            try:
                binx_str, biny_str = bp.split("x")
                sp.binx = int(binx_str)
                sp.biny = int(biny_str)
            except Exception as ex:
                logger.warn("Invalid frame binning '%s': %s; skipping to next scan",
                        bp,
                        ex.message)
                lineno = 0
                continue

        elif lineno == 13:
            # Sample line:
            # 13    duration, secs: 1     
            try:
                sp.dur = _atof(bp)
            except Exception as ex:
                logger.warn("Invalid exposure duration '%s'; skipping to next scan",
                        bp)
                lineno = 0
                continue

        elif lineno == 14:
            # Sample line:
            # 14           shutter: Open

            sp.shutter = ccdStr2SO(bp)
            if sp.shutter == None:
                logger.warn("Invalid shutter option '%s'; skipping to next scan",
                        bp)
                lineno = 0
                continue

        elif lineno == 15:
            # Sample line:
            # 15          ccdcalib: CATALOG

            sp.ccdcalib = ccdStr2Calib(bp)
            if sp.ccdcalib == None:
                logger.warn("Invalid ccdcalib option '%s'; skipping to next scan",
                        bp)
                lineno = 0
                continue

        elif lineno == 16:
            # Sample line:
            # 16            filter: N
            if len(bp) < 1:
                logger.warn("Missing filter; skipping to next scan")
                lineno = 0
                continue
            sp.filter = bp[0]

        elif lineno == 17:
            # Sample line:
            # 17             hcomp: 1
            try:
                sp.cmosmode = _atoi(bp)
            except:
                logger.warn("Invalid CMOS readout mode '%s'; skipping to next scan",
                        bp)
                lineno = 0
                continue

        elif lineno == 18:
            # Sample line:
            # 18   Positioning 2048x2048

            try:
                posx_str, posy_str = bp.split("x")
                sp.posx = int(posx_str)
                sp.posy = int(posy_str)
            except Exception as ex:
                # logger.info('Invalid positioning string: %s, no re-positioning will occur', bp)
                sp.posx = None
                sp.posy = None

        elif lineno == 19:
            # Sample line:
            # 19    Interrupt_Allowed: 1
            try: sp.interrupt_allowed = bool(bp)
            except: sp.interrupt_allowed = True

        elif lineno == 20:
            # Sample line:
            # 20          priority: 10

            try:
                sp.priority = _atoi(bp)
            except:
                logger.warn("Invalid priority value '%s'; skipping to next scan",
                        bp)
                lineno = 0
                continue

        elif lineno == 21:
            # Sample line:
            # 21          pathname: /usr/local/telescope/user/images/gad11500.fts

            sp.imagedn = os.path.dirname(bp)
            if sp.imagedn == "":
                logger.warn("Full image pathname required in '%s'; aborting", bp)
                return return_value_on_error

            sp.imagefn = os.path.basename(bp)
            if sp.imagefn == "":
                logger.warn("Filemame missing from path: '%s'; aborting", bp)
                return return_value_on_error

            break # Finished processing scan

        else:
            logger.warn("BUG! Bogus lineno: '%r'", lineno)
            return return_value_on_error

        # end of long switch() statement
        lineno += 1

    # end while()
    if lineno == LASTLINE:
        return (0, sp, offset)
    else:
        return return_value_on_error


def edb_line_to_body(line):
    """
    Try to parse a DB line in XEphem format, and return an associated instance
    which should be a subclass of ephem.Body. Raise an exception if there is a problem.
    """

    # Fix entries that have extra spaces at the beginning
    line = line.lstrip()

    fields = line.split(",")
    if len(fields) == 2 and fields[1] == 'P':
        # pyephem doesn't seem to handle the 'P' (planet) category
        # correctly, so we'll do it manually here

        planet_name_to_class = {
            "Sun": ephem.Sun,
            "Moon": ephem.Moon,
            "Mercury": ephem.Mercury,
            "Venus": ephem.Venus,
            "Mars": ephem.Mars,
              "Phobos": ephem.Phobos,
              "Deimos": ephem.Deimos,
            "Jupiter": ephem.Jupiter,
              "Io": ephem.Io,
              "Europa": ephem.Europa,
              "Ganymede": ephem.Ganymede,
              "Callisto": ephem.Callisto,
            "Saturn": ephem.Saturn,
              "Mimas": ephem.Mimas,
              "Enceladus": ephem.Enceladus,
              "Tethys": ephem.Tethys,
              "Dione": ephem.Dione,
              "Rhea": ephem.Rhea,
              "Titan": ephem.Titan,
              "Hyperion": ephem.Hyperion,
              "Iapetus": ephem.Iapetus,
            "Uranus": ephem.Uranus,
              "Ariel": ephem.Ariel,
              "Umbriel": ephem.Umbriel,
              "Titania": ephem.Titania,
              "Oberon": ephem.Oberon,
              "Miranda": ephem.Miranda,
            "Neptune": ephem.Neptune,
            "Pluto": ephem.Pluto
        }

        if fields[0] in planet_name_to_class:
            # Create an instance of the associated pyephem class
            # and return it
            return planet_name_to_class[fields[0]]()

    else:
        return ephem.readdb(line)

def ccdStr2SO(s):
    """
    convert the given string to a CCDShutterOptions constant,
    or return None if conversion is not possible
    (based on: libmisc/scan.c)
    """

    s = s.strip().upper()
    str_to_so = {
        "CLOSED": CCDSO_CLOSED,
        "OPEN": CCDSO_OPEN,
        "DBL EXPOSE": CCDSO_DBL,
        "MULTI EXPOSE": CCDSO_MULTI
    }

    if s in str_to_so:
        return str_to_so[s]
    else:
        return None

def ccdSO2Str(so):
    """
    convert a CCDShutterOption constant to a string
    """

    so_to_str = {
        CCDSO_CLOSED: "Closed",
        CCDSO_OPEN: "Open",
        CCDSO_DBL: "Dbl Expose",
        CCDSO_MULTI: "Multi Expose"
    }

    return so_to_str.get(so, "(invalid CCDSO constant)")


def ccdStr2Calib(s):
    """
    convert the given string to a CCDCalib object.
    return the CCDCalib object, or None if there
    was a problem parsing the string
    """

    s = s.strip().upper()

    cp = CCDCalib()
    if s == "NONE":
        cp.newc = CT_NONE
        cp.data = CD_RAW
    elif s == "CATALOG":
        cp.newc = CT_NONE
        cp.data = CD_COOKED
    elif s == "BIAS":
        cp.newc = CT_BIAS
        cp.data = CD_COOKED
    elif s == "THERMAL":
        cp.newc = CT_THERMAL
        cp.data = CD_COOKED
    elif s == "FLAT":
        cp.newc = CT_FLAT
        cp.data = CD_COOKED
    elif s == "BIAS ONLY":
        cp.newc = CT_BIAS
        cp.data = CD_NONE
    elif s == "THERMAL ONLY":
        cp.newc = CT_THERMAL
        cp.data = CD_NONE
    elif s == "FLAT ONLY":
        cp.newc = CT_FLAT
        cp.data = CD_NONE
    elif s == "EXT":
        # value is ok, but do nothing. values will be set from Ext Act
        pass
    else:
        return None

    return cp

def ccdStr2ExtAct(s, cp):
    """
    Convert string to extended action for CCDCalib.
    Modifies input CCDCalib as needed, and returns the new copy.
    Returns None if there is a problem.
    """

    s = s.strip().upper()

    if s == "":
        return cp;

    cp.data = CD_NONE

    if s == "FOCUSPOS":
        cp.newc = CT_FOCUSPOS
    elif s == "FOCUSOFF":
        cp.newc = CT_FOCUSOFF
    elif s == "AUTOFOCUS":
        cp.newc = CT_AUTOFOCUS
    elif s == "FIXEDALTAZ":
        cp.newc = CT_FIXEDALTAZ
    elif s == "CMDLINE":
        cp.newc = CT_EXTCMD
    else:
        return None

    # in all existing ext. cases, we want normal (CATALOG) ccd calibration
    cp.data = CD_COOKED
    return cp

def getExtVal(s, sp):
    """
    Parse the values from the ext value line.
    bp: input line
    sp: scan to modify
    return 0 if ok, -1 if error
    """

    s = s.strip()

    if sp.ccdcalib.newc == CT_FIXEDALTAZ:
        if s == "":
            sp.extcmd = "%d, 0" % NO_ALTAZ_ENTRY
            return 0

    # Note - in the talon code, there's a lot of commented out code.
    # It appears that all of the code paths simply copy the (stripped) external value
    # into the scan, so that's all we'll implement for now
    sp.extcmd = s

    return 0


def _atof(s):
    """
    Roughly mimic the behavior of C's atof() by trying to parse
    anything at the start of a string that looks like a number, leading up 
    to the first whitespace character (or end of string).

    Unlike atof, this still throws a ValueError if the number can't be parsed
    """

    return float(_str_before_whitespace(s))

def _atoi(s):
    """
    Roughly mimic the behavior of C's atoi() by trying to parse
    anything at the start of a string that looks like a number, leading up 
    to the first whitespace character (or end of string).

    Unlike atoi, this still throws a ValueError if the number can't be parsed
    """

    return int(_str_before_whitespace(s))

def _str_before_whitespace(s):
    """
    Return the part of the string that comes before any whitespace character
    (newline, tab, space). If the string has no whitespace characters,
    return the entire string
    """

    return re.sub(r'\s.*', '', s)

