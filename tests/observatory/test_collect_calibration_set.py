import logging
import sys
from pathlib import Path

import pytest

from pyscope.observatory import collect_calibration_set


def test_collect_calibration_set(tmp_path):
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    collect_calibration_set(
        observatory="./tests/bin/simulator_observatory.cfg",
        camera="ccd",
        readouts=[0],
        binnings=["1x1"],
        repeat=1,
        dark_exposures=[1],
        filters=["Ha", "R", "B"],
        filter_exposures=[1, 1, 1],
        filter_brightness=None,
        target_counts=None,
        home_telescope=True,
        check_cooler=False,
        tracking=True,
        dither_radius=10,  # arcseconds
        save_path="./tests/bin/cal_test/",
        new_dir=False,
    )


if __name__ == "__main__":
    test_collect_calibration_set(Path("./tests/bin/cal_test/"))
