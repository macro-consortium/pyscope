import logging
import random
import time


# Average best-focus positions for each filter in the system (matched by filter index)
FOCUS_POSITIONS_BY_FILTER = [
    10000, 
    10100, 
    10200, 
    10000, 
    9000, 
    10000, 
    10100,
    10100,
    10100,
    10100
    ]

# Probability of a successful focus run in a given filter.
# 1.0 = succesful focus every time, 0.0 = failure every time
SUCCESS_PROBABILITY_BY_FILTER = [
    0.9,
    0.5,
    0.9,
    0.9,
    0.8,
    0.7,
    0.9,
    0.8,
    0.6,
    0.8
]

# Deterimes how noisy results should be
BEST_FOCUS_STANDARD_DEVIATION = 50

_camera = None

def initialize(camera):
    """
    This function must be called once during the lifetime of the program
    before attempting to perform an autofocus run.
    """

    global _camera

    _camera = camera

def run_autofocus():
    """
    Perform an autofocus run on the currently selected filter.
    If the run is successful, return the best focus position.
    If the run completed but failed to determine a good focus
    position (e.g. because no stars were found), return None.
    If there was a problem completing the run, raise an Exception.
    """

    logging.info("Running simulated autofocus")

    filter_index = _camera.get_active_filter()

    best_focus = FOCUS_POSITIONS_BY_FILTER[filter_index]
    best_focus += random.normalvariate(best_focus, BEST_FOCUS_STANDARD_DEVIATION)

    success_probability = SUCCESS_PROBABILITY_BY_FILTER[filter_index]

    if random.random() < success_probability:
        logging.info("Focus run SUCCEEDED. Best focus = %s", best_focus)
        return best_focus
    else:
        logging.info("Focus run FAILED")
        return None

def set_exposure_length(exp_length_seconds):
    """
    Set the exposure length that will be used for future
    AutoFocus runs. It can be useful to adjust this value
    based on the filter that is being used for AutoFocus
    (e.g. Luminance vs H-alpha)
    """

    pass

def abort_autofocus():
    """
    Try to stop an in-progress autofocus sequence.
    """

    pass
