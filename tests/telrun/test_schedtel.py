import logging

import pytest
from astropy import coordinates as coord
from astropy import time

from pyscope import logger

# from pyscope.telrun import schedtel, plot_schedule_gantt, plot_schedule_sky
from pyscope.telrun import sch


def test_sch_read():
    logger.setLevel("INFO")
    logger.addHandler(logging.StreamHandler())
    read_sched = sch.read(
        "tests/reference/test_sch.sch",
        location=coord.EarthLocation.of_site("VLA"),
        t0=time.Time.now(),
    )

    for ob in read_sched:
        print(ob.configuration["pm_ra_cosdec"], ob.configuration["pm_dec"])


if __name__ == "__main__":
    test_sch_read()
