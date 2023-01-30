from datetime import datetime, timedelta
import logging

"""
This is an IOTA camera driver for Maxim DL.
Anything in this module beginning with an underscore is a
private part of the implementation, and should not be accessed
directly from the outside. All other names should be part of
the standard Camera programming interface. Alternative
implementations can be provided by other drivers in the future.
"""

_maxim = None  # Reference to MaxIm.Application object
_camera = None # Reference to MaxIm.CCDCamera object
_last_exposure_start_datetime = None  # Used to check that the exposure returned by Maxim was generated after the call to Expose()

def initialize():
    # Only try to import the win32com library if the driver is going to be used
    from win32com.client import Dispatch

    global _maxim
    global _camera

    logging.info("Launching MaxIm.Application")
    _maxim = Dispatch("MaxIm.Application")
    _maxim.LockApp = True # Prevent Maxim from closing on application exit

    logging.info("Launching MaxIm.CCDCamera")
    _camera = Dispatch("MaxIm.CCDCamera")
    _camera.DisableAutoShutdown = True # Prevent camera from disconnecting on application exit

    logging.info("Connecting to camera")
    _camera.LinkEnabled = True
    logging.info("Connected to camera '%s'", _camera.CameraName)
    logging.info("Filters:")

    filter_names = get_filter_names()
    for i in range(len(filter_names)):
        logging.info(" %d: %s", i, filter_names[i])

def start_exposure(exposure_length_seconds, open_shutter):
    """
    Start an exposure

    exposure_length_seconds: the duration of the exposure in decimal seconds
    open_shutter: True if the shutter should be open during the exposure
                  (i.e. a "Light" image) or False if the shutter should be
                  closed (i.e. a "Dark" image)
    """

    global _last_exposure_start_datetime

    # Try to see if this resolves Filter property not being reported
    # correctly in some cases
    filter_index = _camera.Filter
    logging.info("Exposing with filter index %d", filter_index)

    _last_exposure_start_datetime = datetime.utcnow() - timedelta(seconds=3)  # Allow for a small margin of error (clock updates, etc)
    
    _camera.Expose(exposure_length_seconds, open_shutter, filter_index)

def abort_exposure():
    """
    Abort an exposure if one is in progress.
    If no exposure is active, this does nothing.
    """

    _camera.AbortExposure()

def is_exposure_finished():
    """
    Following a call to expose(), this function returns True if an
    image from the latest exposure is ready, or False if the exposure
    is still in progress
    """

    return _camera.ImageReady

def verify_latest_exposure():
    """
    Make sure that the image that was returned by Maxim was in fact generated
    by the most recent call to Expose(). I have seen cases where a camera
    dropout occurs (e.g. if a USB cable gets unplugged and plugged back in)
    where Maxim will claim that an exposure is complete but just return the
    same (old) image over and over again.

    Return without error if the image from Maxim appears to be newer than
    the supplied UTC datetime object based on the DATE-OBS header.
    Raise an exception if the image is older or if there is an error
    accessing the image.
    """

    try:
        image = _camera.Document
    except Exception as ex:
        raise Exception("Unable to access Maxim camera imge: " + str(ex))

    if image is None:
        raise Exception("No current image in Maxim")

    image_timestamp = image.GetFITSKey("DATE-OBS")
    # image_timestamp = image_timestamp[:-4] #fixes ValueError: unconverted data remains
    image_datetime = datetime.strptime(image_timestamp, "%Y-%m-%dT%H:%M:%S.%f")

    logging.info("Image timestamp: %s" , image_timestamp) # Added 1Dec2021 for debugging RLM
    logging.info("Image timestamp UTC: %s", image_datetime)
    logging.info("Last exposure start time UTC: %s", _last_exposure_start_datetime)

    if image_datetime < _last_exposure_start_datetime:
        raise Exception("Image is too old; possibly the result of an earlier exposure. There may be a connection problem with the camera")


def save_image_as_fits(filepath):
    _camera.SaveImage(filepath)

def get_filter_names():
    """
    Return a tuple containing the string name of each filter in
    the corresponding filter wheel slot. For example, this function might return:

    ("Red", "Green", "Blue", "Luminance", "H-alpha", "Empty", "Empty")

    where the filter in slot 0 is Red and the filter in slot 6 is empty (no filter)
    """

    return _camera.FilterNames

def get_active_filter():
    """
    Return the index of the currently selected filter, with 0 being
    the first index. The name of the corresponding filter can be 
    accessed by indexing into the result of get_filter_names()
    """

    return _camera.Filter

def set_active_filter(filter_index):
    """
    Set the active filter to the specified index, starting at 0.
    """

    _camera.Filter = filter_index

def get_ccd_width_pixels():
    """
    Return the number of (unbinned) pixels on the CCD in the X direction
    """

    return _camera.CameraXSize

def get_ccd_height_pixels():
    """
    Return the number of (unbinned) pixels on the CCD in the Y direction
    """

    return _camera.CameraYSize

def set_binning(binning_x, binning_y):
    _camera.BinX = binning_x
    _camera.BinY = binning_y

def set_subframe(start_x, start_y, width, height):
    _camera.StartX = start_x
    _camera.StartY = start_y
    _camera.NumX = width
    _camera.NumY = height

def set_cmosmode(cmosmode):
    _camera.ReadoutMode = cmosmode

def run_pinpoint():
    image = _camera.Document
    image.PinPointSolve()

def pinpoint_status():
    image = _camera.Document
    return image.PinPointStatus

def get_ccd_temperature_celsius():
    """
    Return the temperature of the camera, in degrees celsius
    """

    return _camera.Temperature
    
def get_ccd_guider_temperature_celsius():
    """
    Return the temperature of the camera, in degrees celsius
    """

    return _camera.GuiderTemperature

def set_ccd_temperature_setpoint_celsius(degrees_c):
    """
    Set the setpoint of the CCD cooler, in degrees celsius.
    If degrees_c is None, the cooler will be turned off
    """

    if degrees_c is None:
        _camera.TemperatureSetpoint = 30 # Some cameras respond better to setting a setpoint above ambient as a method for turning off the cooler
        _camera.CoolerOn = False
    else:
        _camera.CoolerOn = True
        if _camera.CoolerOn != True:
            logging.warn("Error turning camera cooler on: set CoolerOn to True, but is not reported as being on")

        _camera.TemperatureSetpoint = degrees_c

def set_ccd_guider_temperature_setpoint_celsius(degrees_c):
    """
    Set the setpoint of the CCD cooler, in degrees celsius.
    If degrees_c is None, the cooler will be turned off
    """

    if degrees_c is None:
        _camera.GuiderTemperatureSetpoint = 30 # Some cameras respond better to setting a setpoint above ambient as a method for turning off the cooler
        _camera.GuiderCoolerOn = False
    else:
        _camera.CoolerOn = True
        if _camera.GuiderCoolerOn != True:
            logging.warn("Error turning camera cooler on: set CoolerOn to True, but is not reported as being on")

        _camera.GuiderTemperatureSetpoint = degrees_c
        
def start_guider_exposure(exposure_length_seconds):
    """
    Start an exposure

    exposure_length_seconds: the duration of the exposure in decimal seconds
    open_shutter: True if the shutter should be open during the exposure
                  (i.e. a "Light" image) or False if the shutter should be
                  closed (i.e. a "Dark" image)
    """

    global _last_exposure_start_datetime

    # Try to see if this resolves Filter property not being reported
    # correctly in some cases
    filter_index = _camera.Filter
    logging.info("Exposing with filter index %d", filter_index)

    _last_exposure_start_datetime = datetime.utcnow() - timedelta(seconds=3)  # Allow for a small margin of error (clock updates, etc)

    _camera.GuiderExpose(exposure_length_seconds)