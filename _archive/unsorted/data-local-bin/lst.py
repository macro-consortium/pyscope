#!/usr/bin/python

# Calculate current lst by default or optionally for another longitude

import sys	# for system connections
from time import gmtime, strftime  # for utc

# Initial parameters

global site_longitude


# Greenwich prime meridian
#site_longitude = 0.0

# Moore Observatory near Crestwood, Kentucky USA
site_longitude = 85.5288888888 

# Mt. Kent Observatory  near Toowoomba, Queensland Australia
# site_longitude = -151.855528 


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
  

# Julian day
# Code from aa.usno.navy.mil/faq/docs/JD_Formula.php
# Valid for CE March 1901 through 2099

def jd(year, month, day, utc):
  k = int(year)
  m = int(month)
  i = int(day)
  j1 = float(367*k)
  j2 = -1.*float( int( ( 7*(k + int((m+9)/12) ) )/4 ) )
  j3 = float(int(275*m/9))
  j4 = 1721013.5 + (utc/24.)
  julian = j1 + j2 + j3 +j4
  return(julian)
         

# Map a time in hours to the range 0 to 24         
         
def map24(hour):

  if hour < 0.0:
    n = int(hour/24.0) - 1
    h24 = hour - n*24.0
    return(h24)
  elif hour > 24.0:
    n = (int) (hour / 24.0) 
    h24 = hour - n*24.0
    return(h24)
  else:
    return(hour)  

# Julian day now
# Use system time and compute the Julian day at this moment
# Code from aa.usno.navy.mil/faq/docs/JD_Formula.php
# Valid for CE March 1901 through 2099

def jdnow():
  t = gmtime()
  year = t.tm_year
  month = t.tm_mon
  day = t.tm_mday
  hour = t.tm_hour
  minute = t.tm_min
  second = t.tm_sec
  yearday = t.tm_yday
  utc = second/3600. + minute/60. + hour
  k = int(year)
  m = int(month)
  i = int(day)
  j1 = float(367*k)
  j2 = -1.*float( int( ( 7*(k + int((m+9)/12) ) )/4 ) )
  j3 = float(i + int(275*m/9))
  j4 = 1721013.5 + (utc/24.)
  julian = j1 + j2 + j3 +j4
  return(julian)

# Julian day today
# Use system time and compute the Julian day number for today at 0h UTC
# Code from aa.usno.navy.mil/faq/docs/JD_Formula.php
# Valid for CE March 1901 through 2099

def jdtoday():
  t = gmtime()
  year = t.tm_year
  month = t.tm_mon
  day = t.tm_mday
  utc = 0.
  k = int(year)
  m = int(month)
  i = int(day)
  j1 = float(367*k)
  j2 = -1.*float( int( ( 7*(k + int((m+9)/12) ) )/4 ) )
  j3 = float(i + int(275*m/9))
  j4 = 1721013.5 + (utc/24.)
  julian = j1 + j2 + j3 +j4
  return(julian)



# Local sidereal time

def lstnow():
  jd = jdtoday()
  ut = utcnow()
  tu = (jd - 2451545.0)/36525.0    
  a0 = 24110.54841 / 3600.
  a1 = 8640184.812866 / 3600.0
  a2 = 0.093104 / 3600.0
  a3 = -6.2e-6 / 3600.0
  t = a0 + a1*tu + a2*tu*tu + a3*tu*tu*tu   
  t0 = map24(t)  
  gst = map24(t0 + ut * 1.002737909)
  lst = (gst - site_longitude / 15.0)
  lst = map24(lst)
  return(lst)


# Format hours as hh:mm:ss.sss string

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
  timestr = "%02d:%02d:%02d%s" % (hr, mn, ss, subsecstr) 
  return timestr

if len(sys.argv) == 1:
  pass
elif len(sys.argv) == 2:
  try:
    site_longitude = float(sys.argv[1])
  except:
    print " "
    print "Usage: lst.py or lst.py longitude (degrees) "
    print " "
    sys.exit("Calculate current lst by default or optionally for another longitude\n")
else:  
  print " "
  print "Usage: lst.py or lst.py longitude (degrees) "
  print " " 
  sys.exit("Calculate current lst by default or optionally for another longitude\n")
    
print hms(lstnow())

exit()




