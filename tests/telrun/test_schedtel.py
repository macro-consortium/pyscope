import pytest

from pyscope.telrun import schedtel


def test_schedtel(tmp_path):
    catalog = "./tests/reference/test_schedtel.cat"
    observatory = "./tests/reference/simulator_observatory.cfg"

    schedule = schedtel(
        catalog=catalog,
        observatory=observatory,
        filename=str(tmp_path) + "test_schedtel.ecsv",
    )
    sch = str(tmp_path) + "test_schedtel.ecsv"

    fig, ax = plot_schedule_gantt(sch, obs)
    fig.savefig(str(tmp_path) + "test_schedtel_gantt.png")

    fig, ax = plot_schedule_sky(sch, obs)
    fig.savefig(str(tmp_path) + "test_schedtel_sky.png")


if __name__ == "__main__":
    test_schedtel("./")
