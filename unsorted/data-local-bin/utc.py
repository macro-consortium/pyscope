#!/usr/bin/python

# Calculate current utc
# This is simplified from lst.py

import sys	# for system connections
from time import gmtime, strftime  # for utc

# Initial parameters


# Coordinated universal time

def utcnow():
  t = gmtime()
  year = t.tm_year
  month = t.tm_mon
  day = t.tm_mday
  hour = t.tm_hour
  minute = t.tm_min
  second = t.tm_sec
  yearday = t.tm_yday
  ut = second/3600. + minute/60. + hour
  return(ut)


# Format hours as hh:mm:ss string

def hms(hours):
  hr = int(hours)
  subhours = abs( hours - float(hr) )
  minutes = subhours * 60.
  mn = int(minutes)
  subminutes = abs( minutes - float(mn) )
  seconds = subminutes * 60.
  ss = int(seconds)
  subseconds = abs( seconds - float(ss) )
  subsecstr = ("%.3f" % (subseconds,)).lstrip('0')
  timestr = "%02d:%02d:%02d" % (hr, mn, ss) 
  return timestr

if len(sys.argv) != 1:
  print " "
  print "Usage: utc.py "
  print " " 
  sys.exit("Calculate current utc\n")
    
print hms(utcnow())

exit()




