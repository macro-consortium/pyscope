#!/usr/bin/env python 

'''
find-transients: Find all instances of objects found in taget images, but not in archive image
It will list both newly-found objects, and objects with significantly different magnitudes
'''
vers = 'find-transients version 1.0, 13 Feb 2017'

import sys,os,glob, warnings
import numpy as np 
from astropy.coordinates import SkyCoord
from astroquery.sdss import SDSS
from astropy import units as u
from astropy.io import fits
from astropy.io.fits import getheader,update,setval
from operator import itemgetter
from optparse import OptionParser



def get_args():
	parser = OptionParser(usage = 'Usage: %prog [options] -a archive.fts target.fts', description='Program %prog',version = vers)
	parser.add_option('-a', dest = 'archive',	 metavar='archive image',									 action = 'store',	   help = 'Archive image [required]') 
	parser.add_option('-d', dest = 'detect',	 metavar='detect threshold',	default = 3.0, type = float, action = 'store',	   help = 'Sextractor detect threshold, sigma [default 3.0]')
	parser.add_option('-s', dest = 'sigma_diff', metavar='min. sigma',			default = 3.0, type = float, action = 'store',	   help = 'Min. sigma for variability [default 3.0 ')
	parser.add_option('-m', dest = 'mag_diff',	 metavar='min. mag diff',		default = 0.50, type = float, action = 'store',		help = 'Min. mag. diff. for variability [default 0.5]')
	parser.add_option('-v', dest = 'verbose',	 metavar='verbose',				default = False,			 action = 'store_true',help=  'Verbose output')
	return parser.parse_args()


def get_hdrdata(ftsfile):
	hdr = getheader(ftsfile, 0)
	jd = hdr['JD']
	date = hdr['DATE-OBS']
	exptime = hdr['EXPTIME']
	filter =  hdr['FILTER'][0]
	airmass = hdr['AIRMASS']
	if 'EGAIN' in hdr:
		egain = hdr['EGAIN']
	else:
		egain = 1.00
	nbin = hdr['XBINNING']	# Assume same for y binning
	if 'CRVAL1' not in hdr:
		sys.exit('No WCS in %s, cannot continue' % ftsfile)
	arcsec_pixel = np.abs(hdr['CDELT1']*3600.)
	ra0 = hdr['CRVAL1']; dec0 = hdr['CRVAL2']
	if 'ZMAG' in hdr:
		zp = hdr['ZMAG']
	else:
		zp =0
	naxis1 = hdr['NAXIS1'] ; naxis2 = hdr['NAXIS2']
	crval1 = hdr['CRVAL1'] ; crval2 = hdr['CRVAL2']
	cdelt1 = hdr['CDELT1'] ; cdelt2 = hdr['CDELT2']
	trim = 60
	ra_range =	[crval1 + (naxis1-trim)*cdelt1/2, crval1 - (naxis1-trim)*cdelt1/2]
	dec_range = [crval2 + (naxis2-trim)*cdelt2/2, crval2 - (naxis2-trim)*cdelt2/2]
	return jd, date, exptime, filter, arcsec_pixel, nbin, airmass, ra0, dec0, ra_range, dec_range, zp, egain

def get_sexinfo(sexname, exptime, scale):
	fn = open(sexname,'r')
	lines = fn.readlines()[15:]
	Nr = []; Ra = []; Dec = []; Snr = []; Flux = []; Fluxerr = []; Fwhm = []; V = []; Verr = []
	for line in lines:
		nr, flux, fluxerr, dum, dum, x_pix, y_pix, ra_deg, dec_deg, profile_x, profile_y, pa, fwhm_pixel, dum, flag = [float(x) for x in line.split()]
		v =	 - 2.5*np.log10(flux/exptime)
		if fluxerr == 0: continue
		snr = flux/fluxerr
		verr =	2.5*(fluxerr/flux)	# Expanding log10(1+x) ~ 2.5x
		Ra.append(ra_deg); Dec.append(dec_deg); Flux.append(flux)
		Fluxerr.append(fluxerr); Fwhm.append(fwhm_pixel * np.abs(scale))
		Snr.append(snr); V.append(v); Verr.append(verr)
	fn.close()
	
	# Trim list to stars by restricting fwhm values
	fwhm_min = 1.4; fwhm_max = 8
	A = list(zip(Ra, Dec, Snr, Flux, Fluxerr, Fwhm, V, Verr)); B = []
	for j in range(len(A)):
		if fwhm_min < A[j][5] < fwhm_max: 
			B.append(A[j])
	Ra, Dec, Snr, Flux, Fluxerr, Fwhm, V, Verr = list(zip(*B))
	V = np.array(V); Verr= np.array(Verr)
	return Ra, Dec, Snr, Flux, Fluxerr, Fwhm, V, Verr

def get_starlist(ftsfile, detect_threshold):
	jd, date, exptime, filter, scale, nbin, airmass, ra0, dec0, ra_range, dec_range, zp, do_not_use_this_gain = get_hdrdata(ftsfile)
	# Run sextractor to find stars
	sexname = os.path.abspath(ftsfile).split('.')[0] + '.sexout'
	if verbose: print('Running sextractor on %s with detection threshold = %.1f sigma' % (ftsfile, detect_threshold))
	os.system('/usr/local/bin/sex %s -c %s -CATALOG_NAME %s -DETECT_THRESH %.1f -VERBOSE_TYPE QUIET' \
	% (ftsfile, sex_path, sexname, detect_threshold) )

	# Get position, magnitude info for each listed star in output file, sort by RA
	ra, dec, snr, flux, fluxerr, fwhm, mag, mag_err = get_sexinfo(sexname, exptime, scale)
	ra, dec, snr, fwhm, mag, mag_err =  list(zip(*sorted(zip(ra, dec, snr, fwhm, mag, mag_err))))
	ra = np.array(ra); dec = np.array(dec); snr = np.array(snr); fwhm = np.array(fwhm); mag = np.array(mag); mag_err = np.array(mag_err)
	# Add ZP magnitude
	if zp !=0:
		mag += zp
	else:
		print('Warning: No ZMAG found in %s, using default value' % ftsfile)
		if filter == 'G':
			mag += 22.2
		elif filter == 'R':
			mag += 21.8
	return	ra_range, dec_range, ra, dec, snr, fwhm, mag, mag_err 

def report_differences(archive_image, target_image):
	''' given an archive and target FITS image, find both variable objects and 'new' (transient) objects '''
	# Generate star lists for archive, target images
	ra_range_a, dec_range_a, ra_a, dec_a, snr_a, fwhm_a, mag_a, mag_err_a = get_starlist(archive_image, detect_threshold)
	jd, date, exptime, filter, arcsec_pixel, nbin, airmass, ra0, dec0, ra_range, dec_range, zp, egain = get_hdrdata(archive_image)
	ra_range, dec_range, ra_t, dec_t, snr_t, fwhm_t, mag_t, mag_err_t = get_starlist(target_image, detect_threshold)
	N_a= len(ra_a); N_t = len(ra_t)
	print('Filter = %s' % filter)
	print('Found %i stars in archive image %s' % (N_a, archive_image))  
	print('Found %i stars in target image  %s' % (N_t, target_image))  
	print() 
	if verbose: 
		print('Archive image stars')
		for j in range(N_a):
			c = SkyCoord(ra_a[j],dec_a[j],unit=(u.deg, u.deg))
			coords = c.to_string(style ='hmsdms', precision=2, sep=':', decimal =False)
			print('%s  %5.2f +/- %5.2f' % (coords, mag_a[j], mag_err_a[j] ))

		print('Target image stars')
		for j in range(N_t):
			c = SkyCoord(ra_t[j],dec_t[j],unit=(u.deg, u.deg))
			coords = c.to_string(style ='hmsdms', precision=2, sep=':', decimal =False)
			print('%s  %5.2f +/- %5.2f' % (coords, mag_t[j],mag_err_t[j] ))
		print()
		 
	#print 'Type	RA (deg)	Dec (deg)	 FWHM_a  FWHM_t  %s_a	 %s_obs	 Sigma ' %(filter,filter)
	#print '--------------------------------------------------------------------'
	print() 
	match = 0; no_match = 0
	for j in range(N_t):
		dra = (ra_a - ra_t[j])*np.cos(dec_a[0]*deg); ddec = dec_a - dec_t[j]
		sepn = np.sqrt( dra**2 + ddec**2) * 3600.
		i = np.argmin(sepn); min_sepn = sepn[i]
		c = SkyCoord(ra_t[j],dec_t[j],unit=(u.deg, u.deg))
		coords = c.to_string(style ='hmsdms', precision=2, sep=':', decimal =False)
		ok = (ra_range[0]  <= ra_t[j]  <= ra_range[1] ) and ( dec_range[0] <= dec_t[j] <= dec_range[1] )
		if ok: # Only consider stars whose coords are on archive image 
			if min_sepn < 2:
				diff = np.abs(mag_a[i]- mag_t[j])
				sigma_diff = diff/mag_err_t[j]
				comment = ''
				if fwhm_a[i] > 3.0: comment = 'Galaxy?'
				if diff > min_mag_diff and sigma_diff > min_sigma_diff: 
					print('Possible variable:  %s   %s = (%.2f vs. %.2f)  FWHM = (%5.2f\", %5.2f\") sigma = %.1f   %s ' % (coords, filter, mag_a[i], mag_t[j], fwhm_a[i], fwhm_t[j], sigma_diff, comment ))
				match  += 1
			else: 
				comment = ''
				if fwhm_t[j] > 3.0: comment = 'Galaxy?'
				print('Possible transient: %s   %s = %.2f  FWHM = %.1f  SNR = %4.1f %s' % (coords, filter, mag_t[j],  fwhm_t[j], snr_t[j], comment))
				no_match += 1
				
	print('-------------------------------------------------------------')
	if no_match == 0:
		print('Image %s: All stars in target image have matches in archive image' % target_image)
	else: 
		print('Image %s: No matches for %i of %i stars in target image' % (target_image, no_match, N_t))
	return

# ========== MAIN ==========

deg = np.pi/180.
verbose = True

# Sextractor config file path
sex_path	= '/usr/local/sextractor/default.sex'

# Get options from command line
(opts, args) = get_args()
target_images = args[0]
archive_image  = opts.archive
min_sigma_diff = opts.sigma_diff
min_mag_diff = opts.mag_diff
verbose = opts.verbose
detect_threshold = opts.detect


target_images = glob.glob(target_images)

for target_image in target_images:
	if target_image != archive_image:
		report_differences(archive_image, target_image)
	




