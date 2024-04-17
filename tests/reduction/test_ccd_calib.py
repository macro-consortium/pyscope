## make image with ccdproc
## calibrate with ccdproc
## calibrate with ccd_calib
## take difference
## if equal, then it passes the test
## Follow guideline Will sent


import os

# matplotlib inline
from matplotlib import pyplot as plt
import numpy as np
from photutils.aperture import EllipticalAperture
from convenience_functions import show_image

# Use custom style for larger fonts and figures
plt.style.use('guide.mplstyle')

# Set up the random number generator, allowing a seed to be set from the environment
seed = os.getenv('GUIDE_RANDOM_SEED', None)

if seed is not None:
    seed = int(seed)
    
# This is the generator to use for any image component which changes in each image, e.g. read noise
# or Poisson error
noise_rng = np.random.default_rng(seed)

synthetic_image = np.zeros([1000, 1000])
show_image(synthetic_image, cmap='gray')