import platform

import pytest

from pyscope.observatory import IPCoverCalibrator


@pytest.mark.skipif(
    platform.node() != "TCC1-MACRO", reason="Only run on TCC1-MACRO"
)
def test_IPCoverCalibrator():
    c = IPCoverCalibrator("192.168.2.22", 2101, 1024)

    c.CalibratorOn(1)
    c.CalibratorOff()

    with pytest.raises(NotImplementedError):
        c.CloseCover()
    with pytest.raises(NotImplementedError):
        c.HaltCover()
    with pytest.raises(NotImplementedError):
        c.OpenCover()

    assert c.Brightness is None
    assert c.CalibratorState is None
    assert c.CoverState is None
    assert c.MaxBrightness == 254

    assert c.tcp_ip is not None
    assert c.tcp_port is not None
    assert c.buffer_size is not None
