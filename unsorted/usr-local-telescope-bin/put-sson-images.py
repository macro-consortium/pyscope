#!/usr/bin/env python

'''
Puts images with 2_ prefix in dated archive directory, reruns wcs using
USNO,zips files, and uploads them to SSON file server

v.1.1 26 Nov 08 RLM  -add wcs
v 1.2 05 May 09 RLM - add path to wcs command, uncompress images if needed
v. 13 07 Dec 15 RLM - changed code from 02 to 07; keep copies in user/images; changed transfer file to telrun.sent
23 Dec 2015 RLM change upload to telrun.now (was telrun.sls, which no longer exists after end of run)
'''

import ftplib
import os
import sys
import traceback
import time
from datetime import datetime, timedelta
from fnmatch import fnmatch
import glob

# Local [deimos] and remote [SSON ftp] params
host = 'sierrastars.exavault.com'
user = 'rigel'
pwd = 'rigeladdy'
sdir = 'ftsFiles'
bindir = '/usr/local/telescope/bin'
imagedir = '/usr/local/telescope/user/images/'
archivedir = '/exports/images/sson'
telrundir = '/usr/local/telescope/archive/telrun'
# String to identify SSON images
match_str = '7_*'

# Construct directory name from current date
def datestr():
	y4 = time.strftime("%Y")
	y2 = y4[2:4]
	dm = time.strftime("%d-%B-")
	return dm+y2

def datestr1():
	y4 = time.strftime("%Y")
	y2 = y4[2:4]
	dm = time.strftime("%d-%b-")
	return dm+y2

""" No longer used 
def gethdr_info(fname):
	os.system("fitsvalue %s OBSERVER OBJECT FILTER EXPTIME > x.tmp" % fname)
	fx = open('x.tmp','r')
	hdr = fx.readlines()
	n = 0
	for hline in hdr:
		obj = hline.rstrip()
		if n == 0:
			observer = obj.replace(' ','_')
		elif n == 1:	
			obj = obj.split('|')
			object = obj[0].replace(' ','')
		elif n == 2: filter = obj
		elif n == 3: exptime = obj
		n += 1
	fx.close()
	os.system("rm x.tmp")
	return (observer,object,filter,exptime)
"""

# Start MAIN program

# Pick date from command argument if present, otherwise construct from current date
if len(sys.argv) == 1:
	cdir = datestr()
else:
	cdir = sys.argv[1]
sson_images = []
try:
# Make archive directory (named by date), copy all sson images to that directory
	wild = imagedir+match_str
	sson_image_list = glob.glob(wild)
	#print(sson_image_list)
	one_day_ago = datetime.now() - timedelta(days = 1)
	#print(one_day_ago)
	for image in sson_image_list:
		filetime = datetime.fromtimestamp(os.path.getctime(image))		
		if filetime > one_day_ago: sson_images.append(image)
		#print(filetime)
	nimage = len(sson_images)
	if nimage > 0:
		adir = "%s/%s" % (archivedir,datestr())
		if not os.path.exists(adir): os.mkdir(adir)
		print("Moving %i sson images to %s" % (nimage,adir))
		for image in sson_images:
			os.system("cp %s %s" % (image, adir))
	
# Compress files using zip, rm the original .fts files
		flist = os.listdir(adir)
		os.chdir(adir)
		for fn in flist:
			fnroot = os.path.splitext(fn)[0]
			fnext = os.path.splitext(fn)[1]
			if fnext == '.fth':
				os.system("%s/fdecompress -r %s" % (bindir,fn) )
				fn = fnroot+".fts"
				print("decompressed %s" % fn)
			os.system("%s/wcs -ow2 -u 0.2 %s" % (bindir,fn) )
			os.system("zip -q %s %s" % (fnroot,fn) )
			os.system("rm %s" % fn)

# Log in to SSON ftp server, mkdir named by current date
		print("Logging in to SSON...")
		ftp = ftplib.FTP(host,user,pwd)
		print(ftp.getwelcome())
		ftp.cwd(sdir)
		if datestr() not in ftp.nlst(): ftp.mkd(datestr())
		ftp.cwd(datestr())
	
# Upload images, telrun file to date-stamped SSON directory
		flist = os.listdir(adir)
		for fn in flist:
			ffull = '%s/%s/%s' % (archivedir,datestr(),fn)
			print("Uploading %s ..." % fn)
			ftp.storbinary('STOR '+fn,open(ffull,'rb'),1024)
		fn = "telrun.now"
		ffull = "%s/telrun.sent" % telrundir
		print("Uploading %s ..." % fn)
		ftp.storbinary('STOR '+fn,open(ffull,'rb'),1024)
		ftp.quit()
finally:
		print("Uploaded %i images" % nimage)

