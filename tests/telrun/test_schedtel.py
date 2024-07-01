import logging
from pathlib import Path

import pytest

from pyscope.telrun import plot_schedule_gantt, plot_schedule_sky, schedtel


def test_schedtel(tmp_path):
    logging.basicConfig(level=logging.INFO)

    catalog = "./tests/bin/test_utstart.cat"
    observatory = "./tests/bin/simulator_observatory.cfg"

    schedule = schedtel(
        catalog=catalog,
        observatory=observatory,
        filename=str(tmp_path) + "test_schedtel.ecsv",
    )

    # schedule = "./tests/bin/test_schedtel.ecsv"

    fig, ax = plot_schedule_gantt(schedule, observatory)
    fig.savefig(str(tmp_path) + "test_schedtel_gantt.png", bbox_inches="tight")

    fig, ax = plot_schedule_sky(schedule, observatory)
    fig.savefig(str(tmp_path) + "test_schedtel_sky.png", bbox_inches="tight")


if __name__ == "__main__":
    test_schedtel("./tests/bin/")
