import pytest
from astropy import coordinates as coord
from astropy import time

from pyscope.telrun import sch


def test_sch(tmp_path):
    read_sched = sch.read(
        "tests/reference/test_sch.sch",
        location=coord.EarthLocation.of_site("VLA"),
        t0=time.Time.now(),
    )

    assert len(read_sched) == 13

    sch.write(read_sched, str(tmp_path) + "test.sch")

    read_sched = sch.read(
        str(tmp_path) + "test.sch",
        location=coord.EarthLocation.of_site("VLA"),
        t0=time.Time.now(),
    )

    assert len(read_sched) == 17
