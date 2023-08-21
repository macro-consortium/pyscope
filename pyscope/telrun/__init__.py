"""telrun test docstring

This is a test docstring for the telrun module."""

import logging

logger = logging.getLogger(__name__)

from .init_dirs import init_remote_dir, init_telrun_dir
from .schedtel import parse_sch_file, plot_schedule_gantt, schedtel
from .startup import start_syncfiles, start_telrun
from .syncfiles import syncfiles
from .telrun_exception import TelrunException
from .telrun_operator import TelrunOperator

__all__ = [
    "init_telrun_dir",
    "init_remote_dir",
    "schedtel",
    "plot_schedule_gantt",
    "parse_sch_file",
    "start_telrun",
    "start_syncfiles",
    "syncfiles",
    "TelrunOperator",
    "TelrunException",
]
