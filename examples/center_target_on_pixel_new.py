#!/usr/bin/env python
# coding: utf-8

# # Center Target on Pixel New (telrun compatible version)
# This script attempts to put a target RA and Dec at a particular pixel position
# (which may be outside the bounds of the physical CCD in the case of an off-axis
# spectrometer fiber).
# 
# The script slews to a target, takes an image, finds a WCS solution and offsets
# the mount to place the target RA/Dec at the requested pixel position. This process
# repeats until the target is positioned within a specified tolerance or the maximum
# number of attempts has been exceeded.
# 
# The target pixel position can be calibrated by manually positioning a star at the
# target position and running the calibrate_target_pixel script.

# # Patch Notes
# 6 Oct 2016 RLM | add object RA/Dec looup using SIMBAD
# 
# 31 May 2021 WWG | notebook version, added telrun compatability

# In[2]:


import relimport

import os,sys,logging
import ephem as ep; import numpy as np
from astropy import coordinates
from iotalib import center_target_pinpoint
from iotalib import config_observatory
from iotalib import config_wcs
from iotalib import convert
from iotalib import observatory
from iotalib import talonwcs
from iotalib import rst


# ##### Set global variables and define some useful functions

# In[3]:


pi = np.pi
deg = pi/180.

# dictionary of ep objects
planets = {'moon':ep.Moon(),'mercury':ep.Mercury(),'venus':ep.Venus(),'mars':ep.Mars(),'jupiter':ep.Jupiter(),
           'saturn':ep.Saturn(),'uranus':ep.Uranus(),'neptune':ep.Neptune(),'pluto':ep.Pluto()}

def hr2hms(rahr):
    return str(ep.hours(rahr*pi/12))
    
def deg2dms(decdeg):
    return str(ep.degrees(decdeg*pi/180.))


# ##### Set the observer parameters, required for ephem to work properly

# In[4]:


observer = ep.Observer()
observer.lat = ep.degrees(str(0.55265/deg))
observer.long = ep.degrees(str(-1.93035/deg))
obsname = 'Gemini Telescope, Winer Observatory'
utdiff = -7; localtimename = 'MST'
observer.date = ep.now()


# ##### Function to find object ra and dec via simbad lookup

# In[5]:


def set_object(objname):
    name = objname.lower()
    if any(name in planet for planet in planets): # planet or moon? simbad can't handle these
        obj = planets[name]
        obj.compute(observer)
        objra = obj.ra; objdec = obj.dec
    else: # simbad object via astropy 
        c = coordinates.SkyCoord.from_name(objname)
        objra = hr2hms(c.ra.hour); objdec = deg2dms(c.dec.deg)
        db_str = '%s,f|M|x,%s,%s,0.0,2000' % (objname,objra,objdec)
        obj = ep.readdb(db_str)
        obj.compute(observer)
    return objra,objdec,obj


# ##### Main script with configuration values for standalone version as the defaults

# In[8]:


def center_target_script(object_name='', # name for simbad lookup, if empty then use provided coordinates
        target_ra_j2k_hrs='', # ra coordinates of target in j2k
        target_dec_j2k_deg='', # dec coordinates of target in j2k
        target_pixel_x_unbinned=2048, # target x pixel
        target_pixel_y_unbinned=2048, # target y pixel
        initial_offset_dec_arcmin=0.0, # offset in arcmins for first image to avoid blooming on bright targets
        check_and_refine=True, # if true, continue imaging and recentering until max attempts or within tolerance,
                                 # if false, image and recenter once without checking
        max_attempts=5, # max attempts before script ends
        tolerance_pixels=1, # continue refining until target ra/dec within this many pixels of the target pixel
        exposure_length=5, # exposure length of test images in seconds
        binning=1, # image binning (high binning = low resolution, fast readout)
        save_images=False, # if true, each image is saved to path below
        save_path_template=r'{MyDocuments}\CenterTargetData\{Timestamp}',
        verbose_wcs=True, # output from wcs will be shown in the console
        search_radius_degs=1, # search up to this far from center coordinates before giving up
        sync_mount=False, # entire coordinate system of mount will be offset (offsets apply to future slews)
        telrun=False): # true if telrun is calling the script
    
    # don't attempt to start programs if telrun is calling, configure logging to print and log to file
    if not telrun:
        logging.basicConfig(level=logging.INFO, format='%(message)s', filename='../logs/center_target_script.log',
                           filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logging.getLogger('').addHandler(console)
        
        config_observatory.read()
        config_wcs.read()
        observatory.setup_mount()
        observatory.setup_camera()
    
    # get object name from either telrun, config file, user input, or command line argument
    if object_name == '' and target_ra_j2k_hrs == '' and target_dec_j2k_deg == '':
        try:
            objname = sys.argv[1]
        except: 
            objname = input('Enter target name: ')
    else:
        objname = object_name
    
    logging.info('Running center_target_script for %s...' % objname)
    
    # grabs specified coordinates, or attempts to look up the object in simbad if there are none 
    if target_ra_j2k_hrs != '' and target_dec_j2k_deg != '':
        target_ra_j2k_hrs = convert.from_dms(target_ra_j2k_hrs)
        target_dec_j2k_deg = convert.from_dms(target_dec_j2k_deg)
    else:
        logging.info('Looking up %s in SIMBAD...' % objname)
        target_ra_j2k_hrs, target_dec_j2k_deg, obj = set_object(objname)
        logging.info('Found %s - RA: %s, Dec: %s (J2000)' % (objname, target_ra_j2k_hrs, target_dec_j2k_deg))
        target_ra_j2k_hrs = convert.from_dms(target_ra_j2k_hrs)
        target_dec_j2k_deg = convert.from_dms(target_dec_j2k_deg)
    
    result = center_target_pinpoint.center_coordinates_on_pixel(target_ra_j2k_hrs, target_dec_j2k_deg, 
            target_pixel_x_unbinned, target_pixel_y_unbinned, initial_offset_dec_arcmin, check_and_refine,
            max_attempts, tolerance_pixels, exposure_length, binning, save_images, save_path_template, verbose_wcs,
            search_radius_degs, sync_mount)
    
    if result:
        logging.info('FINAL RESULT: Recentering succeeded')
    else:
        logging.info('FINAL RESULT: Recentering failed')

# %%
if __name__ == "__main__":
    center_target_script(object_name='1E 0754+39.3')
    
# %%

# %%
