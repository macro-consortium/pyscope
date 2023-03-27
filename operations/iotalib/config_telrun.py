"""
Read and validate the expected config files from telrun.cfg
"""

import types

from . import config

values = None
valid_config = False

def read():
    global values
    global valid_config

    values = config.read("telrun.cfg")

    values.require_float("autofocus_exposure_length_seconds", min_value=0.1)
    values.require_int("autofocus_filter_index", min_value=0)
    values.require_float("autofocus_interval_seconds")
    values.require_bool("autofocus_before_first_observation")
    values.require_float("autofocus_starting_focus_position")
    values.require_float("autofocus_starting_focus_position_tolerance")
    values.require_float("autofocus_timeout_seconds")
    values.require_float("camera_cooler_celsius")
    values.require_float("camera_cooler_tolerance")
    values.require_bool("wait_for_scan_start_time")
    values.require_bool("wait_for_sun")
    values.require_bool("check_roof_value")
    values.require_bool("update_sls_status_codes")
    values.require_bool("home_mount_at_start")
    values.require_float("camera_timeout_seconds")
    values.require_float("camera_cooler_warning_minutes")
    #values.require_float("resync_mount_after_interval_seconds") # TODO
    values.require_float("recenter_exposure_seconds")
    values.require_int("recenter_exposure_binning")
    values.require_bool("recenter_using_sync")
    values.require("recenter_if_returns_true", types.FunctionType)

    valid_config = True

