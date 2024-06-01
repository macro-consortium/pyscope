import logging
import sys

import pytest

from pyscope.reduction import reduce_calibration_set


def test_reduce_calibration_set(tmp_path):
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    reduce_calibration_set(
        "./tests/bin/cal_test/",
        camera="ccd",
        mode="0",
        pre_normalize=True,
    )


if __name__ == "__main__":
    test_reduce_calibration_set("./tests/bin/cal_test/")
