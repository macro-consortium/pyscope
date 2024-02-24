import pytest
import glob
import shutil
import os
from pyscope.observatory import collect_calibration_set, Observatory


"""Testing this:
- look at test_observatory.py for a good example

- start simulator server
- run collect_calibration_set
- check that the flats, darks
    - ccd master bias
    - cmos master flat-dark
- check that the masters are created in folder

File Naming Convention:
{type}_{filter}_{binning}_{exposure}_{readout}__{repeat}.fts
"""

def test_collect_calibration_set(tmp_path):
    obs = Observatory(config_path="tests/reference/simulator_observatory.cfg")
    obs.connect_all()
    collect_calibration_set(
        # user will input exposure and brightness for every filter
        observatory=obs, 
        camera='cmos',  # if cmos then flat_darks are done, only unique flat exposures
        #  filters     [R,G,B,C,H,O]
        dark_exposures=[1,2,3,4,5,6],  # len of list * repeat = num files in darks folder
        filter_exposures=[1,2,3,4,5,6],  # flat exposures
        filter_brightness=[1,1,1,1,1,1],  # corresponds to the filters in config file
        repeat=1,
        save_path=tmp_path)

    master_flat_dark = glob.glob(f"{tmp_path}/calibration_set_*/masters/master_flat_dark*")
    assert master_flat_dark != []

    collect_calibration_set(
        # user will input exposure and brightness for every filter
        observatory=obs, 
        camera='ccd',  # if cmos then flat_darks are done, only unique flat exposures
        #  filters     [R,G,B,C,H,O]
        dark_exposures=[1,2,3,4,5,6],  # len of list * repeat = num files in darks folder
        filter_exposures=[1,2,3,4,5,6],  # flat exposures
        filter_brightness=[1,1,1,1,1,1],  # corresponds to the filters in config file
        repeat=1,
        save_path=tmp_path)
    
    master_bias = glob.glob(f"{tmp_path}/calibration_set_*/masters/master_bias*")
    assert master_bias != []
    
    print("passed all tests for ccd")
    print("passed all tests!")

    obs.telescope.Park()
    obs.shutdown()
    obs.disconnect_all()
    cwd = os.getcwd()
    shutil.rmtree(os.path.join(cwd, tmp_path))
    return


# if __name__ == "__main__":
#     test_collect_calibration_set('./tmp_dir')

