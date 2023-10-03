import logging
import time

import pytest

from pyscope import logger
from pyscope.observatory import ASCOMCamera, Observatory


def test_observatory(tmp_path):
    logger.setLevel("INFO")
    logger.addHandler(logging.StreamHandler())

    obs = Observatory(config_path="tests/reference/simulator_observatory.cfg")
    obs.save_config("tests/reference/saved_observatory.cfg")
    new_obs = Observatory(config_path="tests/reference/saved_observatory.cfg")
    obs.connect_all()

    assert obs.lst() is not None
    assert obs.sun_altaz() is not None
    assert obs.moon_altaz() is not None
    assert obs.moon_illumination() is not None
    assert obs.get_object_altaz(obj="M1")
    assert obs.get_object_slew(obj="M1")

    obs.start_observing_conditions_thread()
    # obs.start_safety_monitor_thread()

    obs.telescope.Unpark()
    if obs.telescope.CanFindHome:
        obs.telescope.FindHome()
        assert obs.get_current_object() is not None

    obs.run_autofocus(midpoint=5000, exposure=1, use_current_pointing=True)

    old_position = obs.focuser.Position
    obs.set_filter_offset_focuser(filter_index=5)
    assert obs.filter_wheel.Position == 5
    assert obs.focuser.Position != old_position
    obs.slew_to_coordinates(ra=obs.lst(), dec=45)
    obs.start_derotation_thread()
    obs.camera.StartExposure(0.1, True)
    while not obs.camera.ImageReady:
        time.sleep(0.1)
    obs.save_last_image(
        tmp_path + "last_image.fts", frametyp="light", do_fwhm=True, overwrite=True
    )
    obs.stop_derotation_thread()

    assert obs.safety_status() is not None
    assert obs.switch_status() is not None

    obs.take_flats(
        filter_exposure=6 * [0.1],
        filter_brightness=6 * [1],
        readouts=[0],
        repeat=1,
        save_path=tmp_path,
    )

    obs.take_darks(
        exposures=[0.1, 0.2],
        readouts=[0],
        binnings=["1x1"],
        repeat=1,
        save_path=tmp_path,
    )

    # obs.stop_safety_monitor_thread()
    obs.stop_observing_conditions_thread()
    obs.telescope.Park()
    obs.shutdown()
    obs.disconnect_all()


if __name__ == "__main__":
    tmp_path = "tests/reference/"
    test_observatory(tmp_path)
