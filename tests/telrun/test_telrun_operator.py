import json
import logging
import pprint
from pathlib import Path

import pytest
from astropy import time
from astropy import units as u

from pyscope import logger
from pyscope.observatory import Observatory
from pyscope.telrun import TelrunOperator


def test_telrun_operator(tmp_path):
    logger.setLevel("INFO")
    logger.addHandler(logging.StreamHandler())

    # add formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger.handlers[0].setFormatter(formatter)

    t_now = time.Time.now()
    t_mid = time.Time(int(t_now.jd + 1), format="jd")
    new_longitude = t_mid - t_now - 12 * u.hour
    new_longitude = new_longitude.to(u.hour).value * 15 * u.deg

    obs = Observatory(
        config_path="./tests/bin/simulator_observatory.cfg", longitude=new_longitude
    )

    telrun = TelrunOperator(telhome=tmp_path, observatory=obs, gui=False)

    lst = obs.observatory_time.sidereal_time("apparent", longitude=obs.longitude)


if __name__ == "__main__":
    test_telrun_operator(Path("./my_test/").resolve())
