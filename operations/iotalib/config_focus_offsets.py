"""
Read focus offsets for each filter from focus_offsets.cfg
"""

from . import config

values = None
valid_config = False

def read():
    global values
    global valid_config

    values = config.read("focus_offsets.cfg")

    values.require("best_focus_value", dict)

    for key, value in list(values.best_focus_value.items()):
        if type(key) != int or key < 0:
            raise config.ValidationError("All keys in best_focus_value must be positive integers")
        if value is not None and type(value) not in (int, float):
            raise config.ValidationError("All values in best_focus_value must be numbers or None")

    valid_config = True

