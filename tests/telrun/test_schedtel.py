import logging

import pytest
from astropy import coordinates as coord
from astropy import time

from pyscope import logger

# from pyscope.telrun import schedtel, plot_schedule_gantt, plot_schedule_sky
from pyscope.telrun import sch


def test_sch_read():
    read_sched = sch.read(
        "tests/reference/test_sch.sch",
        location=coord.EarthLocation.of_site("VLA"),
        t0=time.Time.now(),
    )

    assert len(read_sched) == 13


def test_sch_write(tmp_path):
    pass
