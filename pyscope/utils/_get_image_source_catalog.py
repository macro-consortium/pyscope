from astropy import convolution, wcs
from astropy.io import fits
import photutils.background as photbackground
import photutils.segmentation as photsegmentation
from photutils.utils import calc_total_error

def _get_image_source_catalog(image_path, box_size=50, filter_size=3, threshold=1.5,
                            kernel_fwhm=3, kernel_size=5, effective_gain=1,
                            connectivity=8, npixels=10, nlevels=32, contrast=0.001):
    '''Finds sources in an image and returns a catalog of their positions
    along with other properties'''

    with fits.open(image_path) as hdul:
        image = hdul[0].data
        image = image.astype(float)
        hdr = hdul[0].header

    bkg = photbackground.Background2D(image, (box_size, box_size), 
                    filter_size=(filter_size, filter_size),
                    bkg_estimator=photbackground.MedianBackground())
    image -= bkg.background

    kernel = photsegmentation.make_2dgaussian_kernel(kernel_fwhm, size=kernel_size)
    convolved_image = convolution.convolve(image, kernel)

    segment_map = photsegmentation.detect_sources(convolved_image, 
                            threshold * bkg.background_rms, 
                            npixels=npixels, 
                            connectivity=int(connectivity))
    segm_deblend = photsegmentation.deblend_sources(convolved_image, segment_map, 
                            connectivity=int(connectivity),
                            npixels=npixels, nlevels=nlevels, contrast=contrast,
                            progress_bar=False)
    
    err = calc_total_error(image, bkg.background_rms, effective_gain)

    cat = photsegmentation.SourceCatalog(image, segm_deblend, convolved_data=convolved_image, 
        background=bkg.background, wcs=wcs.WCS(hdr), error=err)

    return cat