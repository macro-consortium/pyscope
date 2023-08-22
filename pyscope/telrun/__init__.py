"""telrun test docstring

This is a test docstring for the telrun module."""

# isort: skip_file

import logging

logger = logging.getLogger(__name__)

from .telrun_exception import TelrunException
from .exoplanet_transits import exoplanet_transits
from .init_dirs import init_telrun_dir, init_remote_dir
from .rst import rst
from .schedtel import schedtel, plot_schedule_gantt, parse_sch_file
from .startup import start_telrun, start_syncfiles
from .syncfiles import syncfiles
from .telrun_operator import TelrunOperator

__all__ = [
    "exoplanet_transits",
    "init_telrun_dir",
    "init_remote_dir",
    "rst",
    "schedtel",
    "plot_schedule_gantt",
    "parse_sch_file",
    "start_telrun",
    "start_syncfiles",
    "syncfiles",
    "TelrunOperator",
    "TelrunException",
]
