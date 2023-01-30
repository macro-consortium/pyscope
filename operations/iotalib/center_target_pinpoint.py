#!/usr/bin/env python
# coding: utf-8

# # Center Target Notebook
# Utilities for refining telescope pointing by taking images and finding
# WCS solutions

# # Patch Notes
# 31 May 2021 WWG | Notebook version, general cleanup for better compatability with telrun
# 17 Mar 2022 WWG | Pinpoint used to generate WCS headers instead of old WCS routine

# In[1]:


from datetime import datetime
import logging,os,time,tempfile,math

from . import config_observatory
from . import config_wcs
from . import convert
from . import observatory
from . import astropy_wcs


# ##### Function to parse a filepath entry

# In[ ]:


def parse_filepath_template(template):
    my_documents_path = os.path.expanduser(r'~\My Documents')
    timestamp = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    
    template = template.replace('{MyDocuments}', my_documents_path)
    template = template.replace('{Timestamp}', timestamp)
    
    return template


# ##### Main function, default parameters used as standalone
# Take one or more images at a target, solve with WCS, and tweak the telescope pointing
# to put a particular RA/Dec near a particular pixel on the CCD.

# In[ ]:


def center_coordinates_on_pixel(target_ra_j2k_hrs=0, # ra coordinates of target in j2k
    target_dec_j2k_deg=0, # dec coordinates of target in j2k
    target_pixel_x_unbinned=2048, # target x pixel
    target_pixel_y_unbinned=2048, # target y pixel
    initial_offset_dec_arcmin=0, # offset in arcmins for first image to avoid blooming on bright targets
    check_and_refine=True, # if true, continue imaging and recentering until max attempts or within tolerance,
                           # if false, image and recenter once without checking
    max_attempts=5, # max attempts before script ends
    tolerance_pixels=1, # continue refining until target ra/dec within this many pixels of the target pixel
    exposure_length=5, # exposure length of test images in seconds
    binning=1, # image binning (high binning = low resolution, fast readout)
    save_images=False, # if true, each image is saved to path below
    save_path_template=r'{MyDocuments}\CenterTargetData\{Timestamp}',
    console_output=True, # output from wcs will be shown in the console
    search_radius_degs=1, # search up to this far from center coordinates before giving up
    sync_mount=False): # entire coordinate system of mount will be offset (offsets apply to future slews)
    
    # Not all mount drivers support turning tracking on/off.
    # For example, the ASCOM driver for TheSky does not support it.
    # However, if it is supported, make sure tracking is on before slewing
    if observatory.mount.CanSetTracking:
        observatory.mount.Tracking = True
    
    save_path = parse_filepath_template(save_path_template)
    if save_images and not os.path.isdir(save_path):
        logging.info('Creating directory "%s"' % save_path)
        os.makedirs(save_path)
    
    slew_ra_j2k_hrs = target_ra_j2k_hrs
    slew_dec_j2k_deg = target_dec_j2k_deg + initial_offset_dec_arcmin / 60.0
    
    logging.info('Attempting to put RA: %s, Dec %s (J2000) on unbinned pixel %.2f,%.2f' % (
        convert.to_dms(target_ra_j2k_hrs),
        convert.to_dms(target_dec_j2k_deg), 
        target_pixel_x_unbinned,
        target_pixel_y_unbinned))
    if initial_offset_dec_arcmin !=0:
        logging.info('Offsetting first slew by %.3f arcmin' % initial_offset_dec_arcmin)
    
    for attempt_number in range(max_attempts):
        slew_ra_jnow_hrs,slew_dec_jnow_deg = convert.j2000_to_jnow(slew_ra_j2k_hrs, slew_dec_j2k_deg)
        
        if check_and_refine:
            logging.info('Attempt %d of %d' % (attempt_number+1, max_attempts))
        logging.info('Slewing to J2000 %s, %s' % (
            convert.to_dms(slew_ra_j2k_hrs),
            convert.to_dms(slew_dec_j2k_deg)))
        observatory.mount.SlewToCoordinates(slew_ra_jnow_hrs, slew_dec_jnow_deg)
        
        logging.info('Settling for %d seconds...' % config_observatory.settle_time_secs)
        time.sleep(config_observatory.settle_time_secs)
        
        if not check_and_refine and attempt_number > 0:
            logging.info('Single-shot recentering finished')
            return True
        
        logging.info('Taking %d second exposure...' % (exposure_length))
        observatory.camera.set_binning(binning,binning)
        observatory.camera.start_exposure(exposure_length, True)
        while not observatory.camera.is_exposure_finished():
            time.sleep(0.1)
        logging.info('Image complete')
        
        if save_images:
            filename = 'image_%03d.fits' % (attempt_number)
            filepath = os.path.join(save_path, filename)
            logging.info('Saving image to %s' % filepath)
            observatory.camera.save_image_as_fits(filepath)
        
        logging.info('Searching for Pinpoint solution...')
        observatory.camera.run_pinpoint()
        try:
            while observatory.camera.pinpoint_status() == 3:
                time.sleep(0.01)
            if observatory.camera.pinpoint_status() == 2:
                logging.info("Pinpoint solution found! Continuing...")
            else:
                logging.info("Pinpoint solution failed, continuing...")
                continue
        except Exception as exception:
            logging.info("Pinpoint error: %s" % exception)
            continue
        
        tempfilename = os.path.join(tempfile.gettempdir(), 'center_pixel.fits')
        observatory.camera.save_image_as_fits(tempfilename)
        
        target_radec_x_pixel,target_radec_y_pixel = astropy_wcs.radec_to_xy(tempfilename, str(target_ra_j2k_hrs),
                                                        str(target_dec_j2k_deg))
        
        ra_at_target_pixel_j2k_hrs,dec_at_target_pixel_j2k_deg = astropy_wcs.xy_to_radec(tempfilename,
                                                                    target_pixel_x_unbinned/float(binning),
                                                                    target_pixel_y_unbinned/float(binning))
        
        error_x_pixels = target_pixel_x_unbinned - target_radec_x_pixel*binning
        error_y_pixels = target_pixel_y_unbinned - target_radec_y_pixel*binning
        error_ra_hrs = target_ra_j2k_hrs - ra_at_target_pixel_j2k_hrs
        error_dec_deg = target_dec_j2k_deg - dec_at_target_pixel_j2k_deg
        error_ra_arcsec = error_ra_hrs*15*3600
        error_dec_arcsec = error_dec_deg*3600
        
        logging.info('Latest image J2000 Ra/Dec at target pixel %s, %s' % (convert.to_dms(ra_at_target_pixel_j2k_hrs),
                                                                        convert.to_dms(dec_at_target_pixel_j2k_deg)))
        logging.info('Latest image pixel location of target Ra/Dec: %.2f, %.2f' % (target_radec_x_pixel, 
                                                                                  target_radec_y_pixel))
        logging.info('Latest image position error: %.2f pixels X, %.2f pixels Y' % (error_x_pixels, error_y_pixels))
        logging.info('RA error: %.2f arcsec, Dec error: %.2f arcsec' % (error_ra_arcsec, error_dec_arcsec))
        
        if abs(error_x_pixels) < tolerance_pixels and abs(error_y_pixels) < tolerance_pixels:
            break
        
        if sync_mount:
            logging.info('Syncing mount...')
            ra_at_target_jnow_hrs,dec_at_target_jnow_deg = convert.j2000_to_jnow(ra_at_target_pixel_j2k_hrs,
                                                            dec_at_target_pixel_j2k_deg)
            observatory.mount.SyncToCoordinates(ra_at_target_jnow_hrs, dec_at_target_jnow_deg)
        else:
            logging.info('Offsetting slew coordinates...')
            if slew_ra_j2k_hrs+error_ra_hrs > 24: slew_ra_j2k_hrs = slew_ra_j2k_hrs+error_ra_hrs -24 # Handle targets around 0hrs RA
            else: slew_ra_j2k_hrs = slew_ra_j2k_hrs+error_ra_hrs
            slew_dec_j2k_deg = slew_dec_j2k_deg + error_dec_deg
            
    else:
        logging.info('Unable to position target within %.2f pixels after %d attempts. Aborting...' % (tolerance_pixels,
                                                                                                max_attempts))
        return False

    logging.info('Target is now in position after %d attempts' % (attempt_number+1))
    return True


# %%

# %%

# %%
