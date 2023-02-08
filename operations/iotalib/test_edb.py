import logging
import math
import os
import shutil
import signal
import sys
import time

# Third-party imports
import ephem

from . import convert

def run():
    FORMAT = '%(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, stream=sys.stdout)
    
    edb = "4 Vesta,e,7.141805,103.8094,150.8193,2.361808,0,0.08861177,150.0878,11/13/2019, 1/01/2000,H3,0.15,0"
    
    obj = ephem.readdb(edb)
    
    site = ephem.Observer()
    site.date = '2019/12/2 22:20:00'
    site.pressure=0
    
    test(obj, site)
    
    #site.pressure = 1010;
    #test(obj, site)
    
    site.lat = '88:00:00'
    test(obj, site)
    
    #site.epoch = ephem.now()
    #test(obj, site)

def test(obj, site):
    #logging.info("Location: %s, %s" % (config_observatory.values.latitude_degs, config_observatory.values.longitude_degs))
    logging.info("Site: %r" % site)
    
    obj.compute(site)
        
    target_ra_app_hours = convert.rads_to_hours(obj.ra)
    target_dec_app_degs = convert.rads_to_degs(obj.dec)

    (target_ra_j2000_hours, target_dec_j2000_degs) = convert.jnow_to_j2000(target_ra_app_hours, target_dec_app_degs)

    #logging.info("PE Astrometric Geocentric a_ra = %s, a_dec = %s" % (convert.to_dms(convert.rads_to_hours(obj.a_ra)), convert.to_dms(convert.rads_to_degs(obj.a_dec))))
    #logging.info("My J2000 RA = %s, Dec = %s" % (convert.to_dms(target_ra_j2000_hours), convert.to_dms(target_dec_j2000_degs)))
    #logging.info("PE Apparrent Geocentric g_ra = %s, g_dec = %s" % (convert.to_dms(convert.rads_to_hours(obj.g_ra)), convert.to_dms(convert.rads_to_degs(obj.g_dec))))
    #logging.info("My App RA = %s, Dec = %s" % (convert.to_dms(target_ra_app_hours), convert.to_dms(target_dec_app_degs)))
    logging.info("PE Topocentric ra = %s, dec = %s" % (convert.to_dms(convert.rads_to_hours(obj.ra)), convert.to_dms(convert.rads_to_degs(obj.dec))))
    logging.info("Earth dist: %f   Sun dist: %f" % (obj.earth_distance, obj.sun_distance))
    return
    
    
if __name__ == "__main__":
    run()

