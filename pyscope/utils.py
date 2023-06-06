import importlib
import sys

from pyscope.drivers import abstract
from pyscope.drivers import _ascom
# from .observatory import ObservatoryException

def airmass(alt):
    '''Calculates the airmass given an altitude via Pickering 2002'''

    return 1/np.sin((alt/deg + 244/(165+47*(alt/deg)**1.1))*deg)

def get_image_source_catalog(image_path):
    '''Finds sources in an image and returns a catalog of their positions
    along with other properties'''

    with fits.open(image_path) as hdul:
        image = hdul[0].data
        image = image.astype(np.float64)
        hdr = hdul[0].header

    bkg = photbackground.Background2D(image, (50, 50), filter_size=(3, 3),
                    bkg_estimator=photbackground.MedianBackground())
    image -= bkg.background # subtract the background

    kernel = photsegmentation.make_2dgaussian_kernel(3.0, size=5)
    convolved_image = convolution.convolve(image, kernel)

    segment_map = photsegmentation.detect_sources(convolved_image, 1.5 * bkg.background_rms, npixels=10)
    segm_deblend = photsegmentation.deblend_sources(convolved_image, segment_map,
                            npixels=10, nlevels=32, contrast=0.001,
                            progress_bar=False)

    cat = photsegmentation.SourceCatalog(image, segm_deblend, convolved_data=convolved_image, 
        background=bkg.background, wcs=astropy.wcs.WCS(hdr))

    return cat

def _import_driver(driver_name, device, ascom=False):
    '''Imports a driver'''
    if driver_name is None: return None

    if ascom:
        device_class = getattr(_ascom, device)
        return device_class(driver_name)
    else:
        try: 
            device_module = importlib.import_module('pyscope.drivers.%s' % driver_name)
            device_class = getattr(device_module, device)
        except:
            try: 
                spec = importlib.util.spec_from_file_location(driver_name, device)
                device_class = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = device_class
                spec.loader.exec_module(device_class)
            except: 
                return None

    _check_class_inheritance(device_class, device)

    return device_class()

def _check_class_inheritance(device_class, device):
    if not getattr(abstract, device) in device_class.__bases__:
            raise ObservatoryException('Driver %s does not inherit from the required abstract classes' % driver_name)

class ObservatoryException(Exception):
    pass