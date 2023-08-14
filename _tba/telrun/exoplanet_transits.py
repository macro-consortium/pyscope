# written by aurora hiveley, macalester class of 2023

import suntime

### changeable user inputs:

# from robert mutel recommendations
max_mag = 15.0
min_depth = 0.018

dec_cutoff = 45 # angular range of motion of telescope in terms of declination

# date of target observation in UTC, must be formatted as YYYY-MM-DD
# date = "2023-04-25"
date = input("Date of target observation in UTC (formatted YYYY-MM-DD): ")

# long. and lat. coordinates of winer observatory
# delta = long and sirka = lat in etd url
longitude = 249
latitude = 32


### ideally, the user edits nothing below this point, and just has to run all cells

### calculate local sunrise and sunset times

from suntime import Sun
from datetime import datetime, timedelta, timezone

date_obj = datetime.strptime(date, '%Y-%m-%d')

sun = Sun(latitude,longitude)
# in utc
sunrise = sun.get_sunrise_time(date_obj)
sunset = sun.get_sunset_time(date_obj)
sunrise_obj = datetime.strptime(date + " " + sunrise.strftime('%H:%M'), '%Y-%m-%d %H:%M') # turns into string and back again to get rid of margin of error (wrong data type)
sunset_obj = datetime.strptime(date + " " + sunset.strftime('%H:%M'), '%Y-%m-%d %H:%M')

### calculate date to use for url
ref = datetime.strptime("2023-01-01", '%Y-%m-%d')

difference = date_obj - ref
diff_string = str(difference)
nonnumeric = diff_string.index(" ")
diff = int(diff_string[0:nonnumeric])

num = 2459946 + diff - 1  # first number is url date number of 2023-01-01


import pandas as pd
import numpy as np

url = 'http://var2.astro.cz/ETD/predictions.php?JDmidnight=' + str(num) + '.50000&delka=' + str(longitude) + '&sirka=' + str(latitude)

tables = pd.read_html(url)
df1 = tables[2] # 3rd table in code is the one we want. there are other tables that we don't care about

df2 = df1.iloc[::2] # filter out NaNs (horizontal lines in between entries)
df2.columns=df2.iloc[0] 
df2 = df2.drop(0)

df2['V (MAG)'] = pd.to_numeric(df2['V (MAG)'])
df2['DEPTH (MAG)'] = pd.to_numeric(df2['DEPTH (MAG)'])

# filter object name
df2['OBJECT'] = df2['OBJECT'].str.split('b', 1).str[0].str.strip()

# create new column for isolated right ascension
ras = df2['Elements Coords'].str.split('DE', 1).str[0].str.split('RA:', 0).str[1]
df2['RA'] = ras

# create new column for isolated declination angles
decs = df2['Elements Coords'].str.extract(r'\DE: (.+)$')
df2['Declinations'] = decs

# resolves error where some database entries are signless by adding signs
# probably a cleaner way to do this, but if it works, it works
newDecs = []
fullDecs = []
for dec in df2['Declinations']:
  if (dec[0] != "+") and (dec[0] != "-"):
    dec1 = "+" + dec
  else:
    dec1 = dec
  fullDecs.append(dec)
  newDecs.append(dec1[0:4])

df2['DEC'] = fullDecs
df2['Declinations'] = newDecs
df2['Declinations'] = pd.to_numeric(df2['Declinations'])

## turn times into datetime objects so they can be subtracted with ease

# again, maybe there's a more elegant way to do this, but if it works, it works

starts = []
centers = []
ends = []
durations = []

year = date[0:4]

for index,row in df2.iterrows():
  # clean and set center times
  center = row['CENTER (DD.MM. UT/h,A)']
  transit_date = center[0:6] # save this to add to start and end times since not included in original table

  long_center = center[7:]
  if (long_center[1] == ":"):
    center1 = "0" + str(long_center) # adds 0 to front of single digit hours
  else:
    center1 = str(long_center)
  short_center = center1[0:5]

  short_center_formatted = datetime.strptime(year + " " + transit_date + " " + short_center, '%Y %d.%m. %H:%M')
  centers.append(short_center_formatted)

  # clean and set end times
  end = row['END (UT/h,A)']
  if (end[1] == ":"):
    end1 = "0" + end # adds 0 to front of single digit hours
  else:
    end1 = end
  short_end = end1[0:5]
  short_end_timeonly = datetime.strptime(short_end, '%H:%M')
  short_end_formatted = datetime.strptime(year + " " + transit_date + " " + short_end, '%Y %d.%m. %H:%M')
  ends.append(short_end_formatted)

  # clean and set start times
  start = row['BEGIN (UT/h,A)']
  if (start[1] == ":"):
    start1 = "0" + start # adds 0 to front of single digit hours
  else:
    start1 = start
  short_start = start1[0:5]
  short_start_timeonly = datetime.strptime(short_start, '%H:%M')
  
  # handles if transit carries into next day
  if (short_start_timeonly > short_end_timeonly):
    short_start_formatted = datetime.strptime(year + " " + transit_date + " " + short_start, '%Y %d.%m. %H:%M') - timedelta(days = 1)
  else:
    short_start_formatted = datetime.strptime(year + " " + transit_date + " " + short_start, '%Y %d.%m. %H:%M')
  starts.append(short_start_formatted)

  # transit duration calculations
  duration = short_end_formatted - short_start_formatted
  durations.append(str(duration))

df2['Transit Start'] = starts
df2['Transit Center'] = centers
df2['Transit End'] = ends
df2['Duration'] = durations

## filter by magnitude, depth, and declination

df3 = df2[
          # magnitudes must be brighter than cut off
          (df2["V (MAG)"] < max_mag) & 
          # must have depth greater than cut off
          (df2["DEPTH (MAG)"] > min_depth) & 
          # declination within +/- angular cut off of winer
          (abs(df2["Declinations"] - latitude) < dec_cutoff ) & 
          # transit starts after sun sets
          (df2['Transit Start'] > sunset_obj) &  
          # transit ends before sunrise
          (df2['Transit End'] < sunrise_obj) ]

# delete some rows from display to clean it up
df3 = df3.drop(columns = ['BEGIN (UT/h,A)', 'CENTER (DD.MM. UT/h,A)', 'END (UT/h,A)', 'D (min)', 'Elements Coords', 'Declinations'])

print(df3)

