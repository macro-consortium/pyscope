import logging

import pytest

from pyscope.observatory import Observatory
from pyscope.telrun import TelrunOperator


def test_telrun_operator_wcs(tmp_path):
    # set up logging for debugging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    # create a new observatory
    obs = Observatory(config_path="./tests/bin/simulator_observatory.cfg")
    obs.connect_all()

    # create a telrun operator
    telrun = TelrunOperator(telhome=tmp_path, observatory=obs, gui=False)

    # solve
    telrun._async_wcs_solver(
        "./tests/bin/xwg002_fixed.fts",
        target_path="./tests/bin/xwg002_solved.fts",
    )


if __name__ == "__main__":
    test_telrun_operator_wcs("./tests/bin/my_test_dir/")
