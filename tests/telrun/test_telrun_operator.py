import logging

import pytest

from pyscope import logger
from pyscope.observatory import Observatory
from pyscope.telrun import TelrunOperator


def test_dynamic_schedtel(tmp_path):
    pass


def test_telrun_operator(tmp_path):
    logger.setLevel("INFO")
    logger.addHandler(logging.StreamHandler())

    obs = Observatory(config_path="tests/reference/simulator_observatory.cfg")
    obs.connect_all()

    telrun = TelrunOperator(telhome=tmp_path, observatory=obs)


if __name__ == "__main__":
    test_dynamic_schedtel("./my_test/")
