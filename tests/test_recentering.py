# Only necessary for testing development installations of the package
import logging
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib.pyplot as plt

# Import the package modules we need
import pyscope

print(getattr(pyscope, '__version__'))

logging.basicConfig(level=logging.INFO)

# zmags, zmags_err, fig, (ax0, ax1, ax2) = analysis.calc_zmag('tests/xwg206100c.fts', filt='G', threshold=10,
#                     plot=True, verbose=False)
# fig.savefig('tests/test_recentering.png')
# plt.show()

'''
# Initialize the hardware, names can be found using the ProfileExplorer
camera = Camera('ASCOM.DLImaging.Camera', ascom=True)
telescope = Telescope('ASCOM.PWI4.Telescope', ascom=True)
wcs = WCS('wcs_astrometrynet')

# Hand these objects to the observatory and connect to all of them
observatory = Observatory(camera=camera, telescope=telescope, wcs=wcs)
observatory.connect_all()

# Home the telescope
observatory.telescope.FindHome()

# Begin cooling camera
observatory.camera.SetCCDTemperature = -20
while observatory.camera.CCDTemperature > -19:
    print('Cooling camera... %s' % observatory.camera.CCDTemperature)
    time.sleep(30)

# Attempt to recenter the telescope
success = observatory.recenter(obj='M95')
print('The recentering was a success: %s' % success)'''