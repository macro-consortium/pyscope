import platform
import time

import pytest

from pyscope.observatory import PWI4Focuser


@pytest.mark.skipif(platform.node() != "TCC1-MACRO", reason="Only works on TCC1-MACRO")
def test_pwi4_focuser():

    f = PWI4Focuser()
    f.Connected = True
    assert f.Connected == True
    assert f.Absolute == False
    assert f.IsMoving == False

    with pytest.raises(NotImplementedError):
        f.Absolute
        f.MaxIncrement
        f.MaxStep
        f.StepSize
        f.TempComp
        f.TempCompAvailable
        f.Temperature

    f.Move(3000)
    while f.IsMoving:
        time.sleep(1)

    f.Connected = False
    assert f.Connected == False


if __name__ == "__main__":
    test_pwi4_focuser()
