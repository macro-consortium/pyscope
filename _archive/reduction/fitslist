#!/usr/bin/env python

import glob, re, sys, os, warnings
import numpy as np
from astropy.io import fits
from operator import itemgetter
from optparse import OptionParser
from prettytable import PrettyTable, PLAIN_COLUMNS,MARKDOWN,SINGLE_BORDER,DOUBLE_BORDER

import warnings
warnings.simplefilter("ignore", category=RuntimeWarning)  # Avoid annoying warning when computing median of empy array


'''
18-Oct 2016 RLM add try/except to catch bad FITS files.
06-Nov-2016 Fix header to align with columns
1.4   Minor changes for list formatting
1.5  Change to Andor IKON ZP, minor format changes
1.6  Add OBJCTRA, OBJCTDEC as aliases to OBJRA, OBJDEC; allow non-existence of ZMAGERR
1.61 change nominal ZPmags to account to new gain setting on IKON camera
1.7  Change grism filter codes, Ikon-> SBIG6303
1.8  Align output format better, ZPMAG SBIG 6303 -> AC4040
1.81 High StackPro => SPro
1.9  Add binning
1.91 Make keyword CMOSMODE optional for compatibility with older images 
2.0 Use prettytable to format output table so columns line up properly, calculate ZPmag for each gain mode,other small formatting improvements
2.01  Add optional OBJRA, OBJDEC keywords to replace OBJCTRA, OBJCTDEC
'''
vers = '2.01, 3 May 2022'

def get_args():
	parser = OptionParser(description='Program %prog',version = vers)
	parser.add_option('-f', dest = 'filter', metavar='Filter', action = 'store', default = '', help = 'Filter name [default all]') 
	parser.add_option('-v',dest = 'verbose', metavar = 'Verbose', action ='store', default = False, help = 'verbose, default  False')
	return parser.parse_args()
	

# Get offsets from field image
def get_offsets(hdr):
	''' 
	Input : FITS header
	Output  RA, Dec pointing errors [Radians] 
	'''
	deg = np.pi/180. ; arcsec = deg/3600.
	has_wcs = 'CRVAL1' in hdr
	grism = hdr['FILTER'][0] == '8' or hdr['FILTER'][0] == '9'
	if has_wcs and not grism:
		ra0 = float(hdr['CRVAL1']) * deg ; dec0 = float(hdr['CRVAL2']) * deg
		if 'OBJRA' in hdr:
			RA = hdr['OBJRA']; DEC = hdr['OBJDEC']
		else:
			RA = hdr['OBJCTRA']; DEC = hdr['OBJCTDEC']
		ra_hr,ra_min,ra_sec = [float(x) for x in re.split(':| ',RA)]
		dec_deg,dec_min,dec_sec = [float(x) for x in re.split(':| ',DEC)]
		ra = ( ra_hr + ra_min/60. + ra_sec/3600.) * 15 * deg
		sign = -1 if DEC[0]=='-' else 1
		dec  = (dec_deg + sign*dec_min/60. + sign*dec_sec/3600.) *deg
		dra = (ra -ra0) * np.cos(dec0)     ; ddec = (dec - dec0)
		if abs(dra)>999*arcsec : dra =999*arcsec
		if abs(ddec)>999*arcsec: ddec =999*arcsec
	else:
		dra = np.nan; ddec = np.nan
	return dra, ddec

def get_fwhm(hdr):
	# Returns airmass, mean FWHM [arcsec] - actual and zenith corrected
	if 'AIRMASS' in hdr:
		z = hdr['AIRMASS']
	else: 
		z = 1.0
	pixel = hdr['XPIXSZ'] * micron
	grism = hdr['FILTER'][0] == '8' or hdr['FILTER'][0] == '9'
	if 'FWHMH' in hdr and not grism:
		if 'CDELT1' in hdr:
			plate_scale = np.abs(hdr['CDELT1'] * deg/pixel)
		else:
			plate_scale = np.nan
		fh = hdr['FWHMH']; fv = hdr['FWHMV']
		fwhm = np.sqrt(fh * fv) * pixel
		fwhm *= plate_scale/arcsec
		fwhm_zenith = fwhm * (z**-0.6)
	else:
		fwhm = np.nan; fwhm_zenith = np.nan
	return z, fwhm, fwhm_zenith

def get_zp(hdr):
	if 'ZMAG' in hdr:
		zp = hdr['ZMAG']
		if 'ZMAGERR' in hdr: 
			zp_err = hdr['ZMAGERR']
		else:
			zp_err = 0.0
	else:
		zp = np.nan; zp_err = np.nan
	return zp, zp_err

def zp_stats(filter, mode,S):
	Zp = []
	for s in S:
		ftsfile, obj, fil, exp, JD, Date, UT, RA, DEC, Z, fwhm, fwhm_zenith, zp, zperr, moonangl,moonphas,binning,cmos_mode,dx, dy = s
		if fil == filter and cmos_mode == mode: 
			Zp.append(zp)
	zp = np.array(Zp)
	if len(zp) != 0:
		zp_med = np.nanmedian(zp); zp_std = np.nanstd(zp)
	else:
		zp_med = np.nan       ; zp_std = np.nan
	return zp_med, zp_std
	
# ----- MAIN ------

# Conversion constants
micron = 1.e-6
deg = np.pi/180.; arcmin = deg/60.; arcsec = deg/3600.

# Parse options
(opts, args) = get_args()
if len(args) == 0:
	fnames = './*.fts'
else:
	fnames = args[0]                 
if len(opts.filter) == 0:
	filter = ''
else:
	filter = opts.filter[0].upper() 
verbose = opts.verbose

# Spin through FITS files in current directory
ftsfiles = glob.glob(fnames)
S = []
for ftsfile in ftsfiles:
	# Catch fts files with corrupt headers
	try:
		im,hdr = fits.getdata(ftsfile,0,header=True)
	except:
		continue
	try:
		D = hdr['DATE-OBS']; Date = D[0:10]; UT = D[11:-3]; JD = float(hdr['JD'])
		if 'OBJRA' in hdr:
			RA = hdr['OBJRA']; DEC = hdr['OBJDEC']
		else:
			RA = hdr['OBJCTRA']; DEC = hdr['OBJCTDEC']
		obj = hdr['OBJECT'] 
		RA = RA.split('.')[0] ; DEC = DEC.split('.')[0] ; UT =UT.split('.')[0]
		Z, fwhm, fwhm_zenith = get_fwhm(hdr)
		if 'READOUTM' in hdr:
			cmos_mode = hdr['READOUTM']
			if cmos_mode == 'High StackPro': cmos_mode = 'SPro'
		else:
			cmos_mode = '   '
		moonangl = hdr['MOONANGL'] ; moonphas = hdr['MOONPHAS'] 
		dx,dy = get_offsets(hdr)
		fil = hdr['FILTER'][0]
		xbin = hdr['XBINNING'] ; ybin = hdr['YBINNING']
		binning ='%ix%i' % (xbin,ybin)
		exp = hdr['EXPOSURE']
		zp,zperr = get_zp(hdr)
		if filter == fil or filter == '':
			S.append([ftsfile,obj, fil, exp, JD, Date, UT, RA, DEC, Z, fwhm, fwhm_zenith, zp, zperr, moonangl, moonphas, binning, cmos_mode, dx/arcsec, dy/arcsec])
	except:
		if verbose: print('%s: header does not have required keywords, skipping' % ftsfile)

# Sort on JD
print('sorting...')
S = sorted(S,key = itemgetter(4))

T = PrettyTable()
T.set_style(SINGLE_BORDER)

t1 = ['FITS file', 'Object', 'RA', 'Dec', 'Fil', 'Exp', 'Date', 'UT',' Z', 'Moon','Bin', 'Mode']
t2 = ['FWHM', 'FWHM_0','Pointing','ZP magnitude']
T.field_names = t1 + t2


for s in S:
	ftsfile, obj, fil, exp, JD, Date, UT, RA, DEC, Z, fwhm, fwhm_zenith, zp, zperr, moonangl, moonphas,binning, cmos_mode, dx, dy = s
	if np.isnan(zp):
		zpstr = ' '
	else:
		zpstr = '%5.2f +/- %4.2f' % (zp,zperr)
	ftsname = os.path.basename(ftsfile)
	grism = fil=='8' or fil =='9'
	
	angle= '%i' % moonangl + chr(176)
	s1 = [ftsname,  obj, RA, DEC,  fil, '%.1f' % exp, Date,  UT ,'%.1f' % Z, angle, binning, cmos_mode]
	if grism:
		s2 = [' ', ' ',' ',' ']
		T.add_row(s1+s2)
	else:
		
		s2 = ['%.1f\"' % fwhm,'%.1f\"' % fwhm_zenith,'%.0f\",%.0f\"' %(dx, dy), zpstr]
		T.add_row(s1+s2)
T.align['FITS file'] = 'l'
T.align['Exp'] = 'r'
print(T)
print()
print('Number of images = %i' % len(S))
fwhm = [row[10] for row in S]; fwhm_z = [row[11] for row in S]
dx =  [row[14] for row in S]; dy = [row[15] for row in S]
mean_moon_phase = np.median([row[15] for row in S])


print('Median FWHM = %.1f\" +/- %.1f\"  [%.1f\" zenith]' % (np.nanmedian(fwhm),np.nanstd(fwhm), np.nanmedian(fwhm_z)))


print('Mean Moon phase: %.2f' % mean_moon_phase)
print('\nMedian zero-point magnitudes')


T = PrettyTable()
T.set_style(SINGLE_BORDER)
T.field_names =['Gain mode','Filter','Zero-point']
for mode in ['Low','High','SPro']:
	for filter in ['G','R']:
		zp, zp_err =zp_stats(filter,mode,S)
		T.add_row(['%s' % mode,'%s' % filter, '%5.2f +/-%5.2f' % (zp,zp_err)])
print(T)
	
