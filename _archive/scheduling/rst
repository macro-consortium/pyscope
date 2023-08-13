#!/usr/bin/env python

# Calculate the rise, transit, and set times at observatory Obs. for Sun or 
# user-specified source name on current day [default] or user-specified date

# RLM April 12 2008 - added sesame_resolve from KMI
# 13 Sept 2012 convert from pynova to pyephem, clean up code, add planets
# 04 Oct 2014 Rewrite sesame_Resolver to use astropy.query [KMI code no longer worked] RLM
# 07 Oct 2014 added VAO as alternate observatory
# 10 Oct 2014 add UT,LST to dusk, dawn report line; support for object lookup in asteroids.edb, comets.edb
# 22 Nov 2014 add asteroids_dim.edb; hours to date input
# Fix lst format in get_times
# 3 Nov 2015 fix circumpolar objects [start list at sunset]; change reference Rigel to Winer
# 21 Mar 2016 If no object given in command, report LST, UT, MST times of astronomical sunset, sunrise 
# v. 2.0 25 Nov 2019 Fix bug: was returning EOD for solsys objects, now J2000 [.ra to .a_ra etc.]; Add  UT date to list; add optparse 
# v. 2.01 1-Dec-2019 add distance, mag when available
# v. 2,1  18 May 2020 add JPL Horizons lookup, print correct RA/Dec vs hour

from __future__  import print_function
import ephem as ep # pyephem library
import numpy as np
import sys, time,re, os.path
from astroquery.simbad import Simbad
from optparse import OptionParser
from astroquery.jplhorizons import Horizons
from astropy import units as u
from astropy.coordinates import Angle


# suppress warning message when object not found
import warnings
warnings.filterwarnings("ignore")


vers = '2.1 (18 May 2020)'

def get_args():
	usage = "Usage: %prog [options]"
	parser = OptionParser(description='Program %prog. Reports hourly az/el coordinates for a specified object and date at Winer or VAO' ,usage=usage, version = vers)
	parser.add_option('-s', dest = 'source', metavar='Source', default ='',action = 'store',  help = 'Source name [default: just report rise/set times]')
	parser.add_option('-d', dest = 'date', metavar='date'	 , action = 'store', type='string', default = '', help = 'UT date: yyyy/mm/dd [default current night]')
	parser.add_option('-o', dest = 'observatory', metavar='Observatory'	 , action = 'store', type='string', default = 'Winer', help = 'Telescope (VAO, Winer) [default Winer]')
	return parser.parse_args()
	
def sesame_resolve(name):
    objtable = Simbad.query_object(name)
    if objtable == None: sys.exit('Cannot find %s, in Simbad, asteroid, comet, or planet databases, try again' % name)
    objids = Simbad.query_objectids(name)
    ra = float(repr(ep.hours(str(objtable['RA'][0])))) * 12/np.pi
    dec =float(repr(ep.degrees(str(objtable['DEC'][0])))) * 180/np.pi
    #print 'objids =',objids['ID'][0]
    identifiers = objids['ID'][0]  # Returns first ID, don't know how to get list
    return(ra,dec, identifiers)

def get_JPL_object(name,jd):
   
    obj = Horizons(id=name,location='857', id_type = 'smallbody', epochs=jd)
    try:
        eph = obj.ephemerides()
        ra = Angle(np.array(eph['RA'])[0], u.degree)
        ra_str = ra.to_string(unit=u.hour, sep=':',precision=2)
        dec = Angle(np.array(eph['DEC'])[0], u.degree)
        dec_str = dec.to_string(unit=u.degree, sep=':',precision =1)
        return [True,ra_str, dec_str]
    except:
        return [False]

def set_object(objname):
    name = objname.lower()
    JPL_lookup = False
    global jd
    # Planet or moon?  
    if any(name == planet for planet in planets):
        i = planets.index(name)
        obj = ep_planets[i]
        obj.compute(observatory)
        objra = obj.a_ra; objdec = obj.a_dec
        ids = ''
    # JPL Horizons
    elif(get_JPL_object(objname,jd)[0]):
        success, objra, objdec = get_JPL_object(objname,jd)
        JPL_lookup = True
        db_str = '%s,f|M|x,%s,%s,0.0,2000' % (objname,objra,objdec)
        obj = ep.readdb(db_str); obj.compute(observatory)
        ids = ''
    # Asteroid?
    elif any(name == asteroid_name for asteroid_name in a_lower):	
        i = a_lower.index(name)
        obj = ep.readdb(ep_asteroids[i])
        obj.compute(observatory)
        objra = obj.a_ra; objdec = obj.a_dec
        ids = ''
    # Dim asteroid?
    elif any(name == asteroid_name for asteroid_name  in adim_lower):
    	i = adim_lower.index(name)
    	obj = ep.readdb(ep_asteroids_dim[i])
    	obj.compute(observatory)
    	objra = obj.a_ra; objdec = obj.a_dec
    	ids = ''
    # Comet?
    elif any(name == comet_name for comet_name in c_lower):	
        i = c_lower.index(name)
        obj = ep.readdb(ep_comets[i])
        obj.compute(observatory)
        objra = obj.a_ra; objdec = obj.a_dec
        ids = ''
    # Simbad object?
    else:
        (rahr, decdeg, ids) = sesame_resolve(objname)
        objra = hr2hms(rahr); objdec = deg2dms(decdeg)
        db_str = '%s,f|M|x,%s,%s,0.0,2000' % (objname,objra,objdec)
        obj = ep.readdb(db_str); obj.compute(observatory)
    return JPL_lookup, objra, objdec,ids, obj


def hr2hms(rahr):
    rahms = str(ep.hours(rahr*np.pi/12))
    return rahms
   
    
def deg2dms(decdeg):
    decdms = str(ep.degrees(decdeg*np.pi/180.))
    return decdms
  
    
def get_times(t):
    observatory.date = t
    local =  str(ep.Date(observatory.date + utdiff*ep.hour)).split()[1][0:8]
    ut  =    str(t).split()[1][0:8]
    ymd = str(ep.Date(observatory.date)).split()[0]
    hh,mm,ss = str(observatory.sidereal_time()).split(':')
    ss = ss[0:2]
    if len(hh) == 1: hh = '0' + hh
    lst = hh + ':' + mm + ':' + ss
    return ymd,local,ut,lst

# MAIN

deg = np.pi/180.

python_version = sys.version_info.major

# crack args
(opts, args) = get_args()
Obs = opts.observatory.upper()
Src = opts.source
Date = opts.date

# List of planets (& Moon) known to ephem
planets =    ['moon',    'mercury',   'venus',   'mars',     'jupiter',    'saturn',    'uranus',    'neptune',    'pluto']
ep_planets = [ep.Moon(), ep.Mercury(), ep.Venus(), ep.Mars(), ep.Jupiter(), ep.Saturn(), ep.Uranus(), ep.Neptune(), ep.Pluto()]

# Generate database lists of asteroids, comets by reading current catalogs

asteroid_cat = '/usr/local/telescope/archive/catalogs/asteroids.edb'
asteroid_dim_cat = '/usr/local/telescope/archive/catalogs/asteroids_dim.edb'
comet_cat = '/usr/local/telescope/archive/catalogs/comets.edb'
if not os.path.isfile(asteroid_cat): sys.exit('Sorry, %s does not exist on this computer, quitting' % asteroid_cat)

if python_version ==3:
    asteroid_file = open(asteroid_cat,'r', encoding = 'utf-8', errors = 'ignore')
    asteroid_dim_file = open(asteroid_dim_cat,'r', encoding = 'utf-8', errors = 'ignore')
    comet_file     = open(comet_cat,'r', encoding = 'utf-8', errors = 'ignore')
else:
    asteroid_file = open(asteroid_cat,'r')
    asteroid_dim_file = open(asteroid_dim_cat,'r')
    comet_file     = open(comet_cat,'r')

ep_asteroids = [line for line in asteroid_file.readlines() if not line.startswith('#')]
ep_asteroids_dim = [line for line in asteroid_dim_file.readlines() if not line.startswith('#')]
ep_comets =   [line for line in comet_file.readlines() if not line.startswith('#')]
asteroid_names = [a.split(',')[0] for a in ep_asteroids]; a_lower = [s.lower() for s in asteroid_names]
asteroid_dim_names = [a.split(',')[0] for a in ep_asteroids_dim]; adim_lower = [s.lower() for s in asteroid_dim_names]
comet_names = [c.split(',')[0] for c in ep_comets]; c_lower = [s.lower() for s in comet_names]

min_elev = '+10'        # Define minimum observable elevation in degrees
twilight_elev = '-12'  # Define solar elevation at astronomical twilight, when roof opens

# Set observer circumstance to observatory 
observatory  = ep.Observer()

# Which observatory?
if Obs == 'WINER':
	observatory.lat = ep.degrees(str(0.55265/deg))
	observatory.long = ep.degrees(str(-1.93035/deg))
	obsname = 'Gemini Telescope, Winer Obs.'
	utdiff = -7; localtimename = 'MST'
elif Obs == 'VAO':
	observatory.lat = ep.degrees(str(41.841375))
	observatory.long = ep.degrees(str(-90.188328))
	obsname = 'Van Allen Observatory, Iowa City'
	if time.localtime().tm_isdst:
		utdiff = -5; localtimename = 'CDT'
	else:
		utdiff = -6; localtimename = 'CST'	
else:
	sys.exit('Unsupported observatory %s, quitting', Obs)

if Date == '':
	observatory.date = ep.now()
else:
	observatory.date = Date

# Calculate JD and date strings
jd_ep = float(ep.Date(observatory.date)); jd = jd_ep + 2415020
date_str = str(observatory.date).split()[0]

# Check if object was specified. If so, define objname, objra, objdec, ids
if Src != '':
	object = True
	objname = Src
	JPL,objra,objdec,ids,obj = set_object(objname)
else:
	object = False

# Calculate local times of astronomical dusk, dawn on specified date 
sun = ep.Sun()
observatory.horizon = twilight_elev
sun.compute(observatory)
dawn = ep.Date(sun.rise_time + utdiff*ep.hour)  ; dusk = ep.Date(sun.set_time + utdiff*ep.hour)
dawn_str = str(dawn).split()[1][0:8]; dusk_str = str(dusk).split()[1][0:8]

dmy,local_dawn, ut_dawn, lst_dawn = get_times(ep.Date(sun.rise_time))
dmy,local_dusk, ut_dusk, lst_dusk = get_times(ep.Date(sun.set_time))

if object:
	print()
	print('%s' % obsname)
	print('Object = %s, Date: %s JD: %10.3f' % (objname, dmy,jd))
	print('RA(J2000): %s, Dec(J2000): %s [now]' % (objra,objdec))
	if JPL: print('Using JPL Horizons coordinate query')
	try:
		print('Distance = %.2f AU'  % obj.earth_distance, ',  Magnitude = %.1f' % obj.mag)
	except AttributeError:
		print()
	print('Astronomical dusk: %s (%s),  %s (UT),  %s (LST)' % (local_dusk, localtimename,ut_dusk,lst_dusk))
	print('Astronomical dawn: %s (%s),  %s (UT),  %s (LST)' % (local_dawn, localtimename,ut_dawn,lst_dawn))
	print()
	print('  UT Date      JD          UT         %s       LST        Elev    RA(J2000)     Dec(J2000) ' % localtimename)
	print('-------------------------------------------------------------------------------------------') 

	# Print hourly elevations and times when object is above min_elev and time is between dusk and dawn
	observatory.horizon = min_elev
	if not obj.circumpolar:
		observatory.date = obj.rise_time
	else:
		observatory.date = sun.set_time

	nhr = 0 
	for n in range(0,24):
		jd = float(ep.Date(observatory.date)) + 2415020
		if JPL:
			object = Horizons(id=objname,location='857', id_type = 'smallbody', epochs=jd)
			eph = object.ephemerides()
			ra = Angle(np.array(eph['RA'])[0], u.degree)
			ra_str = ra.to_string(unit=u.hour, sep=':',precision=2)
			dec = Angle(np.array(eph['DEC'])[0], u.degree)
			dec_str = dec.to_string(unit=u.degree, sep=':',precision =1)
			db_str = '%s,f|M|x,%s,%s,0.0,2000' % (objname,ra_str,dec_str)
			obj = ep.readdb(db_str)
		obj.compute(observatory)
		sun.compute(observatory)
		eldeg = float(obj.alt)/deg
		elsun = float(sun.alt)/deg
		ymd,local,ut,lst = get_times(observatory.date)
		if eldeg > float(min_elev) and elsun < float(twilight_elev): 
			print('%s  %9.3f  %s  %s  %s      %4.1f    %s   %s' % (ymd,jd, ut,local, lst, eldeg, obj.a_ra, obj.a_dec))
			nhr += 1
		observatory.date += ep.hour
	print()
	# Warnings:  if object is unobservable on requested date, or if transit occours during day
	if nhr == 0:
		print('Warning: Object %s not observable between dusk and dawn on %s' % (objname, str(observatory.date).split()[0]))
	else:
		print('%s is observable for about %i hours on %s' % (objname, nhr, ymd))
		print()
		observatory.date = obj.transit_time
	sun.compute(observatory); elsun = float(sun.alt)/deg
	if elsun > float(twilight_elev):
		t = str(ep.Date(observatory.date + utdiff*ep.hour)).split()[1][0:8]
		print('Warning: Transit occurs during daytime (%s %s), use LSTSTART option when schedling' % (t,localtimename))
	print()
	if ids != ' ': print("Source also known as:")
	print(ids)
	print()
else:
	print()
	print('%s  Date: %s JD: %8.1f' % (obsname,Date ,jd))
	print('Astronomical dusk: %s (%s),  %s (UT),  %s (LST)' % (local_dusk, localtimename,ut_dusk,lst_dusk))
	print('Astronomical dawn: %s (%s),  %s (UT),  %s (LST)' % (local_dawn, localtimename,ut_dawn,lst_dawn))
