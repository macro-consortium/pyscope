#!/usr/bin/env python

# find-asteroid: Finds moving objects by comparing three images, removing fixed stars, and fitting for rectilinear motion in remaining objects
# v. 2.0 RLM Add MPC lookup

import sewpy, sys, os, requests
import numpy as np
from astropy.table import Table
from astropy.coordinates import SkyCoord 
from astropy.io import fits
from optparse import OptionParser
from astropy import units as u



vers ='%prog 2.0 8-Dec-2016'

def get_args():
	global parser
	parser = OptionParser(description='%prog  finds moving object given exactly three input images', version = vers)
	parser.add_option('-f', dest = 'ftsfiles', metavar='FITS images'  , action = 'store', default = '', help = 'comma-separated list of images [required]')
	parser.add_option('-m', dest = 'min_mag', metavar='Minimum mag.'  , action = 'store', type=float, default = 21.0, help = 'Minimum magnitude [default 21.0]')
	parser.add_option('-v', dest = 'verbose', metavar='Verbose', action = 'store_true', default = False, help = 'Verbose output')
	parser.add_option('-r', dest = 'radius', default = 15, metavar='Radius', action = 'store', help='Search radius [arcmin], default 15')
	return parser.parse_args()

def hdr_info(fitsname):
	# Returns header info, substituting default values for zmag if needed
	hdr = fits.open(fitsname)[0].header
	filter = hdr['FILTER'][0]
	z = hdr['AIRMASS']
	exptime = hdr['EXPTIME']
	if filter == 'G': 
		k = 0.28
	elif filter == 'R': 
		k = 0.13
	elif filter == 'W':
		k = 0.05
	elif filter == 'N':
		k = 0.3
	elif filter == 'B':
		k = 0.35
	else:
		k = 0.2
	if 'ZMAG' in hdr:
		zmag = hdr['ZMAG']
	else:
		if filter == 'B': 
			zmag = 20.0
		elif filter == 'G': 
			zmag = 21.05
		elif filter == 'R':
			zmag = 20.20
		elif filter == 'W':
			zmag = 20.65
		elif filter == 'N':
			zmag = 21.8
		else:
			zmag = 20.
	
		print('WARNING: No Zero-point magnitude in header, using assumed zmag = %.2f , k = %.2f based on filter %s' % (zmag, k, filter))
	return zmag, k, exptime, z

def get_hdr_info(ftsfile):
	im,hdr = fits.getdata(ftsfile,0,header=True)
	object = hdr['OBJECT']
	nbin = hdr['XBINNING']
	D = hdr['DATE-OBS']; date = D[0:10]; ut = D[11:]
	ra = hdr['RA']; dec = hdr['DEC']
	exptime = hdr['EXPTIME']
	filter = hdr['FILTER']
	z = hdr['AIRMASS']
	return object, nbin, date, ut, ra, dec, exptime, filter, z
	
def substring(string, i, j):
	return string[i:j]
	
def make2dlist(string):
	objlist = string.split('\n')
	object2d = []
	for index in range(len(objlist) - 1):
		object2d.append([])
		object2d[index].append(substring(str(objlist[index]), 0, 24))
		object2d[index].append(substring(str(objlist[index]), 24, 36))
		object2d[index].append(substring(str(objlist[index]), 36, 47))
		object2d[index].append(substring(str(objlist[index]), 47, 53))
		object2d[index].append(substring(str(objlist[index]), 53, 58))
		object2d[index].append(substring(str(objlist[index]), 59, 65))
		object2d[index].append(substring(str(objlist[index]), 69, 73))
		object2d[index].append(substring(str(objlist[index]), 76, 81))
		object2d[index].append(substring(str(objlist[index]), 82, 86))
		object2d[index].append(substring(str(objlist[index]), 87, len(objlist[index]) - 1))
	del object2d[0:4]
	return object2d

def fix_signs(ra_off,dec_off,ra_dot,dec_dot):
	# Crack crazy suffixs N/S and +/- on MPC offsets, rates
	ra_off = ra_off.strip() ; dec_off = dec_off.strip()
	ra_dot = ra_dot.strip() ; dec_dot = dec_dot.strip()
	if ra_off.endswith('E'):
		ra_off = -1*float(ra_off[:-1])
	else:
		ra_off = float(ra_off[:-1])
	if dec_off.endswith('S'):
		dec_off = -1*float(dec_off[:-1])
	else:
		dec_off = float(dec_off[:-1])
	if ra_dot.endswith('-'):
		ra_dot = -1*float(ra_dot[:-1])
	else:
		ra_dot = float(ra_dot[:-1])
	if dec_dot.endswith('-'):
		dec_dot = -1*float(dec_dot[:-1])
	else:
		dec_dot = float(dec_dot[:-1])
	return ra_off, dec_off, ra_dot, dec_dot

def get_stars(fitsname,theta_max, min_mag):
	'''
	Uses sewpy to retrieves star positions, fluxes from Table T, 
	omitting any with flags != 0, theta > theta_max 
	'''
	zmag, k, exptime, z = hdr_info(fitsname)
	out = sew(fitsname)
	T = out["table"] # this is an astropy table
	adu = T['FLUX_BEST']
	adu = [x/exptime for x in adu]
	mag = zmag - 1.091*np.log(adu) - z * k
	N = len(T); RA_deg = []; Dec_deg  = []; Coords = []; Radius = []; Mag = []
	Flag = T['FLAGS']; radius = T['FLUX_RADIUS']
	for n in range(N):
		if Flag[n] == 0 and radius[n] < theta_max and mag[n] < min_mag:
			ra_deg  = T['ALPHA_J2000'][n]
			dec_deg = T['DELTA_J2000'][n]
			RA_deg.append(ra_deg); Dec_deg.append(dec_deg)
			Coords.append(SkyCoord(ra_deg,dec_deg,unit='deg'))
			Mag.append(mag[n])
			Radius.append(radius[n])
	RA_deg, Dec_deg, Coords, Mag, Radius = list(zip(*sorted(zip(RA_deg, Dec_deg, Coords, Mag, Radius) ) )) # Sort on RA
	return RA_deg, Dec_deg, Coords, Mag, Radius

def chisq(ra,dec,t):
	# Calculates linear fit and chi-square to ra vs time, dec vs. time, assuming origin is at first point
	ra = np.array(ra); dec = np.array(dec)
	dt = t[1:] - t[0]
	ra_dot = ( np.sum( ra[1:]*dt) -  ra[0]*np.sum(dt) ) / np.sum(dt**2)
	dec_dot = ( np.sum(dec[1:]*dt) - dec[0]*np.sum(dt) ) / np.sum(dt**2)
	ra_mod  =  ra[0] + ra_dot * (t - t[0])
	dec_mod = dec[0] + dec_dot * (t - t[0])
	chisq = (1./(len(t)-2)) * np.sum( (ra_mod - ra)**2  + (dec_mod - dec)**2 )
	return chisq, ra_dot, dec_dot

def compare_2fields(j, k):
	# Returns indices of stars in field j that are and are not in field k
	global Coords, Nstars, max_sepn
	ra0 = np.array([s.ra.deg for s in Coords[j]]) ; dec0 = np.array([s.dec.deg for s in Coords[j]])
	ra1 = np.array([s.ra.deg for s in Coords[k]]) ; dec1 = np.array([s.dec.deg for s in Coords[k]])
	indices_match = []; indices_nomatch = []
	for i in range(Nstars[j]):	
		dra = np.abs(ra1-ra0[i]); ddec = np.abs(dec1-dec0[i])
		s = np.sqrt(dra**2 + ddec**2)
		found = np.any(s < max_sepn) 
		if found:
			indices_match.append(i)
		else:
			indices_nomatch.append(i)
	return indices_match, indices_nomatch

def find_no_match():
	# Find indices of stars in fields  that are not in either of the other 2 fields		
	dum,no_match01 = compare_2fields(0,1); dum,no_match02 = compare_2fields(0,2)
	no_match0 = list(set(no_match01).intersection(no_match02))
	dum,no_match10 = compare_2fields(1,0); dum,no_match12 = compare_2fields(1,2)
	no_match1 = list(set(no_match10).intersection(no_match12))
	dum,no_match20 = compare_2fields(2,0); dum,no_match21 = compare_2fields(2,1)
	no_match2 = list(set(no_match20).intersection(no_match21))
	return [no_match0,no_match1,no_match2]

def find_mpc_objects(ftsfile, radius, limmag):
	''' Query the MPC database for small bodies within a specified radius [arcmin] and limiting magnitude of the center of a FITS image '''
	Objects = []; Obj_Coords = []; Magnitudes = []; Offsets = []; Rates = []; Comments = [] 
	object, nbin, date, ut, ra, dec, exptime, filter, z = get_hdr_info(ftsfile)
	year, month, day = [int(s) for s in date.split('-')]
	uth, utm, uts = [float(s) for s in ut.split(':')]
	day += (uth + utm/60. + uts/3600.) /24.; day ='%.2f' % day
	coord = '%s %s' % (ra, dec); Ctr_Coords = SkyCoord(coord, unit=(u.hourangle, u.deg))
	ra = ra.replace(':',' '); dec = dec.replace(':',' ')
	payload = {"year": year, "month": month, "day": day, "which": "pos", "ra": ra, "decl": dec, "TextArea": " ", "radius": radius, "limit": limmag,\
	"oc": "857", "sort": "d", "mot": "h", "tmot": "s", "pdes": "u", "needed": "f", "ps": "n", "type": "p"}
	r = requests.get('http://www.minorplanetcenter.net/cgi-bin/mpcheck.cgi', params=payload)
	myString=r.text
	#check to see if any objects found
	if "No known minor planets" in r.text:
		return Objects, Ctr_Coords, Obj_Coords, Magnitudes, Offsets, Rates, Comments
	else:
		mySubString=r.text[r.text.find("<pre>")+5:r.text.find("</pre>")]
		mySubString = mySubString.replace('&#176;','d')
		mySubString = mySubString.replace('<a href="http://www.cfa.harvard.edu/iau/info/FurtherObs.html">Further observations?</a>',"")
		#make a 2d list of objects for manipulation by other programs
		objectlist = make2dlist(mySubString)
		for line in objectlist:
			objname, ra, dec, mag, ra_off, dec_off, ra_dot, dec_dot, dum, comment = line
			ra_off, dec_off, ra_dot, dec_dot = fix_signs(ra_off, dec_off, ra_dot,dec_dot)	
			mag = float(mag)
			Objects.append(objname)
			coord = '%s %s' % (ra, dec)
			c = SkyCoord(coord, unit=(u.hourangle, u.deg)); Obj_Coords.append(c)
			Magnitudes.append(mag)
			Offsets.append([ra_off, dec_off]) 
			Rates.append([ra_dot, dec_dot])
			Comments.append(comment)
	return Objects, Ctr_Coords, Obj_Coords, Magnitudes, Offsets, Rates, Comments


# ======= MAIN =============

max_sepn = 1/3600.  # Max separation for match, deg
theta_max = 1.0     # Set largest allowable star width [pixels

# Parse command line arguments
(opts, args) = get_args()
ftsfiles  = opts.ftsfiles.split(',')
Nfts = len(ftsfiles)
if len(ftsfiles) != 3:
	sys.exit('Exactly 3 FITS image names (comma separated) need to be given (option -f), try again') 
min_mag = opts.min_mag
verbose = opts.verbose
search_radius = opts.radius

# Define Sextractor dictionary items to retrieve
sew = sewpy.SEW(params=["ALPHA_J2000", "DELTA_J2000", "FLUX_RADIUS(3)", "FLUX_BEST", "FLAGS"],
        config={"DETECT_MINAREA":5, "PHOT_FLUXFRAC":"0.3, 0.5, 0.7"})

# Loop through FITS files, getting lists of star positions and fluxes
Coords = []; Coords_hms= []; ADU = []; Nstars = []; Radius =[]; Mag = []; jd  = []; RA_deg = []; Dec_deg = []
j = 0

print('Sampling images for objects...')
for ftsfile in ftsfiles:	
	if not os.path.isfile(ftsfile): sys.exit('File %s not found, exiting' % ftsfile)
	hdr = fits.open(ftsfile)[0].header
	jd.append(hdr['JD'])
	ra_deg, dec_deg, coords, mag, radius = get_stars(ftsfile,theta_max, min_mag)	
	Radius.append(radius)
	Mag.append(mag); RA_deg.append(ra_deg); Dec_deg.append(dec_deg)
	Coords.append(coords)
	c = [s.to_string(style ='hmsdms', precision=2, sep=':', decimal=False) for s in coords]
	Coords_hms.append(c)
	Nstars.append(len(mag))
	print('%i stars found in FITS image %s' % ( Nstars[j], ftsfile ))
	j+= 1
print()
print('Looking for moving objects...')
no_match = find_no_match()

if verbose:
	# Print all stars found in each field
	for k in range(3):
		print('Field %i stars' % k)
		for j in range(Nstars[k]):
			print('%s   %.2f' % (Coords_hms[k][j], Mag[k][j]))
		print()

	# Print star in each field that have no matching stars
	for k in range(3):
		print('Image: %s - stars with no matches' % ftsfiles[k])
		no_match[k].sort()
		for j in no_match[k]:
			print('%s   %.2f' % (Coords_hms[k][j], Mag[k][j]))

# Build lists of star coordinates [deg] for non-matching stars in each field
ra0 = []; dec0 = []; ra1 = []; dec1 = [] ; ra2 = []; dec2 = [];
for k in no_match[0]:
	ra0.append(RA_deg[0][k]); dec0.append(Dec_deg[0][k])
for k in no_match[1]:
	ra1.append(RA_deg[1][k]); dec1.append(Dec_deg[1][k])
for k in no_match[2]:
	ra2.append(RA_deg[2][k]); dec2.append(Dec_deg[2][k])

# Print solutions for any no-match stars sets that lie along a linear trajectory 
print() 
k_found = 0; ra_found = [] ; dec_found = []
for k0 in range(len(ra0)):
	for k1 in range(len(ra1)):
		for k2 in range(len(ra2)):
			ra =  np.array( [  ra0[k0],  ra1[k1],  ra2[k2] ])
			dec = np.array( [ dec0[k0], dec1[k1], dec2[k2] ])
			t =   np.array(     [jd[0],    jd[1],    jd[2] ])
			chi,ra_dot,dec_dot = chisq(ra,dec,t)
			chi *= 1.e6
			if chi< 0.1:
				print('Object nr. %i, unnormalized chisq = %.2e' % (k_found+1, chi))
				print('Image %s:   %10.4f   %s    %.2f' % ( ftsfiles[0], jd[0], Coords_hms[0][no_match[0][k0]], Mag[0][no_match[0][k0]] ))
				print('Image %s:   %10.4f   %s    %.2f' % ( ftsfiles[1], jd[1], Coords_hms[1][no_match[1][k1]], Mag[1][no_match[1][k1]] ))
				print('Image %s:   %10.4f   %s    %.2f' % ( ftsfiles[2], jd[2], Coords_hms[2][no_match[2][k2]], Mag[2][no_match[2][k2]] ))
				print('Motion: RA = %.1f\"/hr, Dec = %.1f\"/hr' % (ra_dot*3600/24., dec_dot*3600/24.))
				ra_found.append(ra0[k0])
				dec_found.append(dec0[k0])
				k_found += 1
				print()

# Now perform MPC query of first field, report results
print('Looking for known objects using MPC online query...')
ftsfile = ftsfiles[0]
object, nbin, date, ut, ra, dec, exptime, filter, z = get_hdr_info(ftsfile)	
Objects, Ctr_Coords, Obj_Coords, Magnitudes, Offsets, Rates, Comments = find_mpc_objects(ftsfile, search_radius, min_mag)
ctr_coords = Ctr_Coords.to_string(style ='hmsdms', precision=1, sep=':', decimal =False)
ra_mpc = []; dec_mpc = []

# Print results
N = len(Objects)
if N == 0:
	print("No known minor bodies with V < %s  within %s\' radius of %s on %s at %s UT" % \
	(min_mag, search_radius, ctr_coords, date, ut))
else:
	print()
	print("MPC query found %i minor bodies with V < %s  within %s\' radius of field center (%s) on %s at %s UT" % \
	(N,min_mag, search_radius, ctr_coords, date, ut))
	print()
	print(' Number   Name               V       RA(J2000)    Dec(J2000)      Offsets            Motion        Comment')
	print('----------------------------------------------------------------------------------------------------------------------')
	for j in range(N):
		coords_hmsdms = Obj_Coords[j].to_string(style ='hmsdms', precision=1, sep=':', decimal =False)
		ra_mpc.append(Obj_Coords[j].ra.degree) ; dec_mpc.append(Obj_Coords[j].dec.degree)
		coords = Obj_Coords[j].to_string(style ='hmsdms', precision=2, sep=':', decimal =False)
		ra_off, dec_off = Offsets[j]; ra_rate, dec_rate = Rates[j]
		print('%s   %.2f    %s   [%5.1f\',%5.1f\']   [%3i\"/hr, %3i\"/hr]   %s' % \
		(Objects[j], Magnitudes[j], coords, ra_off, dec_off, ra_rate, dec_rate, Comments[j]))
print() 
ra_mpc = np.array(ra_mpc); dec_mpc = np.array(dec_mpc)
max_sepn = 5/3600.
print('Object matches') 
print('----------------------------------------------------------------------------------')
# Spin through found objects , print matches to MPC objects
if k_found > 0:
	for k in range(k_found):
		dra = np.abs(ra_found[k] - ra_mpc); ddec = np.abs(dec_found[k] - dec_mpc)
		s = np.sqrt(dra**2 + ddec**2)
		index = np.where(s < max_sepn)
		if index[0].size > 0:
			j = np.min(index)
			coords = Obj_Coords[j].to_string(style ='hmsdms', precision=2, sep=':', decimal =False) 
			print('Object %i matches position of %s at %s' % (k+1, Objects[j].strip(), coords))
		else:
			print('Object %i has no MPC match (New discovery?)' % (k+1))
else:
	print('No matches found')