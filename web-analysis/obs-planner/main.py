#!/usr/bin/env python
# coding: utf-8

'''
obsplanner: IRO Observing planner. Uses web interface.
N.B. libraries astroplan, pywebio, jplephem must be installed.
*** NB requires astroquery version 4.3+  [this is required for JPL Horizons planet lookup to work correctly]

v. 0.9 3 Feb 2022 RLM
'''

import numpy as np
from astropy.time import Time
from obsplanner_lib import obs_planner
from obsplanner_utilities import get_inputs, get_recommendation

import matplotlib
import matplotlib.pyplot as plt

#from pywebio.input import *
from pywebio.output import put_text, put_image, put_buttons, put_table, put_link
from pywebio import config,start_server
from pywebio.input import TEXT, FLOAT
import pywebio.input as pywebio_input
import pywebio.session as session

import astropy.units as u
from astropy.coordinates import Angle, SkyCoord, EarthLocation, get_moon, solar_system_ephemeris, get_body

import warnings

matplotlib.use('agg')  # required, use a non-interactive backend
warnings.filterwarnings("ignore")  # Suppress warning from axis projections

# Choose a pretty theme (current choices: dark, yeti,sketchy, minty)
theme = 'dark'
if theme == 'dark':
    title_style ='color: yellow'
else:
    title_style ='color: black'

warning_style = 'color:red'
 
# Set title that appears in web tab
@config(title='Iowa Robotic Observatory Observing Planner',theme=theme) 
def main():
    
    # Define constants
    arcsec = np.pi/(180*3600)
    
    # Add a banner
    iro_banner = '/home/www/cgi-bin/astrolab/iro-banner.png'
    #iro_banner= 'iro-banner.png'
    put_image( open(iro_banner, 'rb').read() )  
    
    # TBD Add link to JPL Horizons web tool 
    # put_link('Inputs (Click for compatible solar system object names',url='https://ssd.jpl.nasa.gov/horizons/app.html#/')

    # Get inputs from webpage
    object_name, telescope, obsdate, myfilter, seeing, detailed = get_inputs() 
    detailed = detailed != []
    myfilter = myfilter.upper()
    fwhm = seeing * arcsec # Convert to radians
    time = Time(obsdate, scale='utc')
    
    # Set camera and gain mode
    if 'Gemini' in telescope:
        camera = 'AC4040'
        mode = 'Spro'  # Fixed mode (for now) to  Spro only
    else:
        camera = 'SBIG6303'
        mode = 'Default'
     
    # Instantiate obs_planner class
    B = obs_planner(telescope, camera, object_name, myfilter, fwhm, time)
    
    # Get some observer, object info
    observer, obsname, obscode, description, min_elevation = B.observatory_info()
    coords, coords_string, magnitude, objtype, is_extended, diameter, sp_type, \
    moon_illum, moon_angle, solar_system_object = B.object_info()
    
    # Warn if object is below minimum observable elevation for entire night: User needs to refresh page and start over
    def reset_form(dummy):
        session.run_js('window.close()')
    object_up_times, object_up_hrs = B.object_up()
    if  object_up_hrs == 0:
        s1 = '%s is below minimum observable elevation, cannot observe from %s. ' %\
        (object_name,telescope)
        s2 = 'Refresh webpage to start over' 
        s = s1+s2
        put_buttons([dict(label=s, value='dummy',color='danger')], onclick=reset_form)
        session.hold()
    
    # Get magnitude from user if magnitude lookup wasn't successful
    if np.isnan(magnitude) or magnitude is None:
        put_text(' ')
        magnitude = pywebio_input.input('Could not find a magnitude for %s, please enter:' % object_name,type=FLOAT)
        B.set_magnitude(magnitude)

    # Report coordinates, object identification, number of hours object is above minimum elevation
    put_text(' ')
    put_text('Summary Information').style(title_style)
    put_text('%s Coordinates(J2000): %s' % (object_name, coords_string))
    if is_extended:
        put_text('Object type: %s, Magnitude = %.1f, diameter %.1f arcmin' % (objtype,magnitude,diameter))
    else:        
        put_text('Object type: %s, Magnitude = %.1f ' % (objtype, magnitude)) 
    put_text('%s is above minimum elevation (%i deg) for %.1f hours' % (object_name, min_elevation, object_up_hrs))
 
    # Report moon stats, proximity to object; warn user if close
    if detailed:
        put_text('Moon illumination: %i%%' % ( moon_illum*100))
        put_text('Moon separation from object %s: %i\N{DEGREE SIGN}' % (object_name, moon_angle))
    if moon_illum > 0.50 and moon_angle < 45 and object_name.casefold() != 'Moon'.casefold():
        put_text('WARNING: Moon is bright and close to your object (%i degrees). \
        This will likely adversely affect image quality' % moon_angle).style(warning_style)

    # Rise/set table sunrise, sunset defined by solar elev = -12 deg; object rise/set define by observatory's min. elev.
    put_text('Rise and Set Times for Sun, Moon, %s at %s' % (object_name, obsname) ).style(title_style)
    A = B.rise_set_table()
    put_table(A[1:], header = A[0])
    
    # Coordinates table if solar system object
    if detailed and solar_system_object:
        put_text('Coordinates vs. UT (querying JPL Horizons...)').style(title_style)
        A = B.coordinates_table(ntimes_per_hr =2)
        put_table(A[1:], header = A[0])
                 
    # Display clear sky plot from ClearDarkSky website if observing is for tonight and observer requests detailed view
    if detailed:
        put_text(' ')
        put_text('Clear Sky predicted observing conditions for next several nights').style(title_style)
        if 'Gemini' in telescope:
            clearsky_image = 'https://www.cleardarksky.com/c/WnrObAZcsk.gif?c=1159225'
            clearsky_webpage ='http://www.cleardarksky.com/c/WnrObAZkey.html'
            put_image(clearsky_image)
        else:
            clearsky_image = 'https://www.cleardarksky.com/c/IwCtyIAcsk.gif?c=1764035'
            clearsky_webpage ='http://www.cleardarksky.com/c/IwCtyIAkey.html'
            put_image(clearsky_image)
        put_link('Click to visit ClearSky webpage for more details',url=clearsky_webpage,new_window=True)

    # Plot airmass vs time 
    put_text(' ')
    put_text('Airmass vs. UT. Note: %s is only observable within times with darkest shading.' % object_name).style(title_style)
    buf = B.airmass_plot()
    s = '%s Airmass plot' % object_name
    put_image(buf.getvalue(),title=s)
    
    # Optionally plot track of object on sky chart and a finding chart
    if detailed:
        # Sky track
        put_text(' ')
        put_text('%s Track on Sky. Note: Points are spaced hourly.' % object_name).style(title_style)
        buf = B.sky_plot()
        put_image(buf.getvalue())
    
        # 10'x10' DSS image
        put_text(' ')
        put_text('10x10 arcmin finding chart for %s [Note: Solar System objects will not appear]' \
        % object_name).style(title_style)
        buf = B.image_field_plot()
        if buf != None:
            put_image(buf.getvalue())
    
    # Report some recommendations for exposure time and filters
    put_text(' ')
    put_text('Recommendations and Observing Notes').style(title_style)
    recommend_string = get_recommendation(object_name, objtype, is_extended, B, mode, seeing, myfilter,magnitude)
    put_text(recommend_string)

    # Optionally plot SNR vs. exposure time and table of sky conditions, SNR [point sources only]
    if not is_extended and detailed:
        # Plot SNR vs exposure time
        put_text(' ')
        put_text('Signal to Noise Ratio vs. Exposure time Plot').style(title_style)
        buf = B.snr_plot(mode)
        put_image(buf.getvalue())
 
        # Table of sky conditions, ADU, and saturation times
        put_text('Use this table and graph to determine suitable exposure times')
        put_text(' ')
        A,saturation_time = B.photometry_summary_table(mode)
        put_text('Saturation exposure time = %.1f sec' % saturation_time)
        put_table(A[1:], header = A[0])
 
if __name__ == "__main__":
    main()

#start_server(main, port=8080, debug=True)

