import pytest

from pyscope.telrun import schedtel


def test_schedtel(tmp_path):
    catalog = "./tests/reference/test_schedtel.cat"
    observatory = "./tests/reference/simulator_observatory.cfg"

    schedule = schedtel(catalog=catalog, observatory=observatory)
    for sb in schedule.scheduled_blocks:
        print(sb.target.ra.to_string(sep="hms"), sb.start_time.isot)


if __name__ == "__main__":
    test_schedtel("")
