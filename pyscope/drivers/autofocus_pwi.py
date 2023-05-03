import logging
import time

# from win32com.client import Dispatch
def Dispatch(com_object_name):
    return None

class Autofocus:
    pass

_autofocus = None # Holds a reference to the PlaneWave.AutoFocus object once initialized

def initialize():
    """
    This function must be called once during the lifetime of the program
    before attempting to perform an autofocus run.
    """

    global _autofocus

    logging.info("Initializing PlaneWave AutoFocus library")
    _autofocus = Dispatch("PlaneWave.AutoFocus")

    logging.info("Starting PWI if needed")
    _autofocus.StartPwiIfNeeded
    _consume_planewave_autofocus_messages()

    logging.info("Connecting to focuser if needed")
    _autofocus.ConnectFocuser
    _consume_planewave_autofocus_messages()

    # Wait up to 3 seconds for a confirmed connection between
    # PWI and the focuser
    for attempt in range(30):
        if _autofocus.IsFocuserConnected:
            logging.info("Focuser is connected")
            break
        time.sleep(0.1)
        _consume_planewave_autofocus_messages()

    if not _autofocus.IsFocuserConnected:
        raise Exception("Unable to connect to focuser while initializing Planewave AutoFocus")

    # We want to have control over the filter that is being used
    # during a focus run
    _autofocus.PreventFilterChange = True

def run_autofocus(timeout_seconds=-1):
    """
    Perform an autofocus run on the currently selected filter.
    If the run is successful, return the best focus position.
    If the run completed but failed to determine a good focus
    position (e.g. because no stars were found), return None.
    If there was a problem completing the run, raise an Exception.
    """

    global _autofocus

    logging.info("Attempting to run PlaneWave AutoFocus")

    if _autofocus is None:
        initialize()
        
    if not _autofocus.IsFocuserConnected:
        raise Exception("Unable to run PlaneWave AutoFocus: focuser is not connected")

    logging.info("Beginning AutoFocus")
    _autofocus.StartAutoFocus

    start_time = time.time()

    while _autofocus.IsAutoFocusRunning:
        _consume_planewave_autofocus_messages()
        time.sleep(0.2)

        if timeout_seconds > 0:
            running_time = time.time() - start_time
            if running_time > timeout_seconds:
                raise Exception("Autofocus took longer than " + timeout_seconds + " seconds to complete")

    succeededOrFailed = "FAILED"
    if _autofocus.Success:
        succeededOrFailed = "SUCCEEDED"

    logging.info("AutoFocus run " + succeededOrFailed)

    if _autofocus.Success:
        return _autofocus.BestPosition
    else:
        return None

def abort_autofocus():
    """
    Try to stop an in-progress autofocus sequence.
    """

    # pywin32 seems to get confused about no-argument methods provided by 
    # some COM servers, treating them as getter properties rather than methods.
    # As a result, simply accessing the name of the method ends up calling it.
    # Here's a trick for handling either case (simply accessing the method name,
    # or calling it using method syntax)
    abortfunc = _autofocus.StopAutofocus
    if hasattr(abortfunc, '__call__'):
        abortfunc()


def set_exposure_length(exp_length_seconds):
    """
    Set the exposure length that will be used for future
    AutoFocus runs. It can be useful to adjust this value
    based on the filter that is being used for AutoFocus
    (e.g. Luminance vs H-alpha)
    """

    _autofocus.ExposureLengthSeconds = exp_length_seconds

def _consume_planewave_autofocus_messages():
    """
    Read any pending messages queued by the autofocus object
    and send them to our log
    """

    while True:
        log_line = _autofocus.NextLogMessage
        if log_line is None:
            return
        logging.info(log_line)
