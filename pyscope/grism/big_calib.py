from pyscope.grism.grism_calib import *
import numpy as np
import matplotlib.pyplot as plt
import csv
import glob
import re
from astropy.io import fits


# define directory
dir = '/Users/crinkosk/pyscope/pyscope/pyscope/grism/temp_images/2024-05-10/'
cal = '/Users/crinkosk/pyscope/pyscope/pyscope/grism/temp_cal/grism_cal(HD124320).csv'

# use glob to find all images in directory
print('getting images...')
image_list = sorted(glob.glob(dir+'*hrg*_cal.fts',recursive=True))
number = [len(image_list)]

print(f'{number} images found')

#initialize lists for averaging
good_params = []
good_coeffs = []
good_fits = []

print('running cailbration routines...')

#quick fix for missing object names
for image in image_list:
    # Function to extract object name from the filename
    def extract_object_name(filename):
        # Assuming the object name is between underscores in the filename
        # Modify the pattern according to the actual structure of your filenames
        pattern = r'grismCalibration_(.*?)_'
        match = re.search(pattern, filename)
        if match:
            return match.group(1)
        else:
            raise ValueError("Object name not found in filename")

    im, hdr = getdata(image, 0, header=True)
    object_name = hdr['OBJECT']

    if object_name == '':
        print('Object name missing from header...')
        obj_name = extract_object_name(image)

        # Open the FITS file
        with fits.open(image, mode='update') as hdul:
            # Add or update the OBJECT keyword in the header
            hdul[0].header['OBJECT'] = obj_name
            # Save changes to the FITS file
            hdul.flush()

        print(f"Object name '{object_name}' has been added to the FITS header.")

    output = doCal(image,cal,[656.45,686.9],[656,687],'High',False)
    mybox, rotangle, x, fit, params, coefficients = output


    good_fits.append(fit)
    good_coeffs.append(coefficients)
    good_params.append(params)

print('-------------------------------------------------------')
print('combining...')
#compile and average arrays
good_fits = np.stack(good_fits)
gain_curve = np.mean(good_fits,axis=0)

good_coeffs =np.stack(good_coeffs)
gain_coeffs = np.mean(good_coeffs,axis=0)

good_params =np.stack(good_params)
wave_coeffs = np.mean(good_params,axis=0)

#plot
plt.plot(x, gain_curve, color='red', label=f'final gain curve')
plt.legend()
plt.xlabel('Wavelength')
plt.ylabel('Gain')
plt.title('Polynomial Gain Curve')
plt.show()

print(f'{number} images were used to compute final calibration')

#writeout to cal file
print('writing to cal file...')
with open(f'/Users/crinkosk/pyscope/pyscope/pyscope/grism/temp_cal/hrg_grism_cal(master).csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([f'Grism calibration created using python'])
        writer.writerow(mybox)
        writer.writerow([rotangle])
        writer.writerow(wave_coeffs)
        writer.writerow(gain_coeffs)
