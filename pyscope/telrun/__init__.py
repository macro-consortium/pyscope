"""telrun test docstring

This is a test docstring for the telrun module."""

# isort: skip_file

import logging

logger = logging.getLogger(__name__)

from .telrun_exception import TelrunException
from .exoplanet_transits import exoplanet_transits
from .init_dirs import init_telrun_dir, init_remote_dir
from .mk_mosaic_schedule import mk_mosaic_schedule
from .rst import rst
from . import sch
from .validate_ob import validate_ob
from .schedtel import schedtel, plot_schedule_gantt, plot_schedule_sky
from .startup import start_telrun, start_syncfiles
from .summary_report import summary_report
from .syncfiles import syncfiles
from .telrun_operator import TelrunOperator

__all__ = [
    "exoplanet_transits",
    "init_telrun_dir",
    "init_remote_dir",
    "mk_mosaic_schedule",
    "rst",
    "sch",
    "validate_ob",
    "schedtel",
    "plot_schedule_gantt",
    "start_telrun",
    "start_syncfiles",
    "summary_report",
    "syncfiles",
    "TelrunOperator",
    "TelrunException",
]
