from astropy import convolution, wcs
from astropy.io import fits
import photutils.background as photbackground
import photutils.segmentation as photsegmentation

def get_image_source_catalog(image_path):
    '''Finds sources in an image and returns a catalog of their positions
    along with other properties'''

    with fits.open(image_path) as hdul:
        image = hdul[0].data
        image = image.astype(np.float64)
        hdr = hdul[0].header

    bkg = photbackground.Background2D(image, (50, 50), filter_size=(3, 3),
                    bkg_estimator=photbackground.MedianBackground())
    image -= bkg.background

    kernel = photsegmentation.make_2dgaussian_kernel(3.0, size=5)
    convolved_image = convolution.convolve(image, kernel)

    segment_map = photsegmentation.detect_sources(convolved_image, 1.5 * bkg.background_rms, npixels=10)
    segm_deblend = photsegmentation.deblend_sources(convolved_image, segment_map,
                            npixels=10, nlevels=32, contrast=0.001,
                            progress_bar=False)

    cat = photsegmentation.SourceCatalog(image, segm_deblend, convolved_data=convolved_image, 
        background=bkg.background, wcs=wcs.WCS(hdr))

    return cat