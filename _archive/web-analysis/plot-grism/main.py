'''
main

Last Updated 12/07/22
University Of Iowa Department of Physics and Astronomy
Robert Mutel
Will Golay
AJ Serck
Jack Kelley
'''

# Python imports
from datetime import date, timedelta, datetime
import astropy.io.fits as pyfits
import os

# Custom libraries
from bin.grism_analysis_web import grism_web
from bin.grism_tools_lib import grism_tools
from config import setup_config

def main():
    home_path = os.path.dirname(os.path.abspath(__file__))+'/'
    cfg = setup_config.read(home_path+'config/plot-grism.cfg')
    default_temp_dir = home_path + cfg.get('default', 'default_temp_dir')
    default_calibration_dir = home_path + cfg.get('default', 'default_calibration_dir')
    default_image_dir = home_path + cfg.get('default', 'default_image_dir')
    day_iter = int(cfg.get('default', 'find_calib_by_date'))
    take_input = bool(cfg.get('default', 'take_input')=='True')
    web_analyzer = grism_web(default_temp_dir, default_image_dir)

    if take_input:
        fits_image, calibration = web_analyzer.get_fits() # Get initial fits image
        if fits_image != None:           
            with open(default_temp_dir+'im.fts', 'wb') as binary_file: # Write fits image to file so it can be analyzed
                binary_file.write(fits_image['content'])
                path_to_fits = default_temp_dir+'im.fts'
        else:
            path_to_fits = default_image_dir + 'sample.fts'
    
        if calibration == None: 
            
            # Get date of image to iterate back to latest calibration file, parse header into date object
            hdulist = pyfits.open(path_to_fits)
            fitsDate = hdulist[0].header['DATE-OBS']
            startDate = date(int(fitsDate[0:4]), int(fitsDate[5:7]), int(fitsDate[8:10]))
            
            # Iterate to find latest calib file in last n days
            if day_iter > 0:
                for testDate in (startDate - timedelta(n) for n in range(day_iter)):
                    if os.path.isfile(default_calibration_dir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'):
                        cal_file = default_calibration_dir+'grism_cal_6_'+testDate.strftime('%Y_%m_%d')+'.csv'
                        break
                    else: continue
                else:
                    web_analyzer.raise_error('No calibration file found for this great image')
                    return
            else:
                web_analyzer.raise_error('No calibration file found for this image')
                return
        elif calibration == 'sample':
            cal_file = default_image_dir+'sample.csv'
        else:
            with open(default_temp_dir+'cal.csv', 'wb') as binary_file:
                binary_file.write(calibration['content'])
                cal_file = default_temp_dir+'cal.csv'
    else:
        cal_file = default_image_dir+'sample.csv'

    grism_analyzer = grism_tools(path_to_fits, cal_file) # instantiate analyzer with fits image and calibration file
    web_analyzer.run_analysis(grism_analyzer)

if __name__ == '__main__':
    main()