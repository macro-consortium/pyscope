import logging
from pathlib import Path

import pytest

from pyscope import logger
from pyscope.telrun import init_telrun_dir


def test_init_telrun_dir(tmp_path):
    init_telrun_dir(tmp_path / "my_test")

    pass


if __name__ == "__main__":
    test_init_telrun_dir(Path("./"))
