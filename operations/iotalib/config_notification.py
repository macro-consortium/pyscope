"""
Read and validate the expected config files from notification.cfg
"""

from . import config

values = None
valid_config = False

def read():
    global values
    global valid_config

    values = config.read("notification.cfg")

    values.require("simulate_email", bool)
    values.require_string("gmail_username")
    values.require_string("gmail_password")
    values.require_list("info_emails", str)
    values.require_list("error_emails", str)
    values.require_int("warning_email_min_interval_seconds")

    valid_config = True

