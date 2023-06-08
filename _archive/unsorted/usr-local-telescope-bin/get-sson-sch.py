#!/usr/bin/env python

# Version 1.0 RLM 1 Nov 2008
# v. 1.1 Changed match prefix to 7_ (was 2_)
#v. 2.0 Updated to python 3.  Josh Kamp

import ftplib
import os
import sys
import traceback
import time
import fnmatch

def handleDownload(block):
	block = block.decode('utf-8')
	file.write(block)

# Construct directory name from current date
def datestr():
	y4 = time.strftime("%Y")
	y2 = y4[2:4]
	dm = time.strftime("%d-%B-")
	print(dm+y2)
	return dm+y2
	
if len(sys.argv) == 1:
	cdir = datestr()
else:
	cdir = sys.argv[1]
print(cdir)

print("Logging in to SSON...")
host = 'sierrastars.exavault.com'
user = 'rigel'
pwd = 'rigeladdy'
sdir = 'schFiles'
match_str = '7_*'

# Put schedules in local netin directory
schdir = '/usr/local/telescope/user/schedin/netin'
os.chdir(schdir)

# Login
try:
	ftp = ftplib.FTP(host,user,pwd)
	print(ftp.getwelcome())
	ftp.cwd(sdir)
	fl = ftp.nlst()
	if cdir in fl:
		ftp.cwd(cdir)
		fl = ftp.nlst()
		flist = fnmatch.filter(fl,match_str)
		if len(flist) > 0:
			for j in range(len(flist)):
				fn = flist[j]
				print("Retrieving %s" % fn)
				file = open(fn,'w')
				f= ftp.retrbinary('RETR '+fn,handleDownload)
				file.close()
		else:
			print("No schedules for Gemini telescope found in %s" % cdir)
	else:
		print("No directory %s at SSON, quitting" % cdir)
	ftp.quit()
finally:
	print("All done...")
	
