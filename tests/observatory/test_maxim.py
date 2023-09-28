import platform
import time

import pytest

from pyscope.observatory import Maxim


@pytest.skipif(platform.system() != "Windows", reason="Maxim only runs on Windows")
def test_maxim():
    m = Maxim()
    assert m.Connected
    assert m.name == "MaxIm DL"
    assert m.app is not None
    assert m.autofocus is not None
    m.Connected = False


@pytest.skipif(platform.system() != "Windows", reason="Maxim only runs on Windows")
def test_maxim_autofocus():
    m = Maxim()
    success = m.autofocus.Run(exposure=1)
    assert success is not None

    with pytest.raises(NotImplementedError):
        m.autofocus.Abort()

    m.Connected = False


@pytest.skipif(platform.system() != "Windows", reason="Maxim only runs on Windows")
def test_maxim_camera():
    m = Maxim()
    c = m.camera
    c.Connected = True
    assert c.Connected
    assert c.Name is not None

    c.StartExposure(1, True)
    time.sleep(0.5)
    if c.CanStopExposure:
        c.StopExposure()

    c.StartExposure(1, False)
    time.sleep(0.5)
    if c.CanAbortExposure:
        c.AbortExposure()

    with pytest.raises(NotImplementedError):
        c.PulseGuide(0, 0)

    with pytest.raises(NotImplementedError):
        c.BayerOffsetX = 0

    with pytest.raises(NotImplementedError):
        c.BayerOffsetY = 0

    c.BinX = 2
    assert c.BinX == 2
    if not c.CanAsymmetricBin:
        assert c.BinY == 2
    else:
        assert c.BinY == 1

    with pytest.raises(NotImplementedError):
        c.CanFastReadout

    assert c.CameraState is not None

    assert c.CameraXSize is not None
    assert c.CameraYSize is not None

    assert c.CanGetCoolerPower

    assert not c.CanPulseGuide

    if c.CanSetCCDTemperature:
        c.SetCCDTemperature = -20
        assert c.SetCCDTemperature == -20

    assert c.CCDTemperature is not None

    c.CoolerOn = True
    assert c.CoolerOn
    assert c.CoolerPower is not None
    c.CoolerOn = False
    assert not c.CoolerOn

    with pytest.raises(NotImplementedError):
        c.ElectronsPerADU
    with pytest.raises(NotImplementedError):
        c.ExposureMax
    with pytest.raises(NotImplementedError):
        c.ExposureMin
    with pytest.raises(NotImplementedError):
        c.ExposureResolution

    with pytest.raises(DeprecationWarning):
        c.FastReadout
    with pytest.raises(DeprecationWarning):
        c.FastReadout = True

    with pytest.raises(NotImplementedError):
        c.FullWellCapacity

    c.Gain = c.Gains[0]
    assert c.Gain == c.Gains[0]

    with pytest.raises(NotImplementedError):
        c.GainMax
    with pytest.raises(NotImplementedError):
        c.GainMin

    assert c.HasShutter is not None
    assert c.HeatSinkTemperature is not None

    c.StartExposure(0.1, True)
    while not c.ImageReady:
        time.sleep(0.1)
    assert c.ImageArray is not None

    with pytest.raises(NotImplementedError):
        c.IsPulseGuiding

    assert c.LastExposureDuration is not None
    assert c.LastExposureStartTime is not None

    with pytest.raises(NotImplementedError):
        c.MaxADU

    assert c.MaxBinX is not None
    assert c.MaxBinY is not None

    c.NumX = 100
    assert c.NumX == 100
    c.NumY = 100
    assert c.NumY == 100

    with pytest.raises(NotImplementedError):
        c.Offset
    with pytest.raises(NotImplementedError):
        c.Offset = 1
    with pytest.raises(NotImplementedError):
        c.OffsetMax
    with pytest.raises(NotImplementedError):
        c.OffsetMin
    with pytest.raises(NotImplementedError):
        c.Offsets
    with pytest.raises(NotImplementedError):
        c.PercentCompleted

    assert c.PixelSizeX is not None
    assert c.PixelSizeY is not None

    c.ReadoutMode = 0
    assert c.ReadoutMode == 0
    assert c.ReadoutModes is not None

    with pytest.raises(NotImplementedError):
        c.SensorName
    with pytest.raises(NotImplementedError):
        c.SensorType

    c.StartX = 1
    assert c.StartX == 1
    c.StartY = 1
    assert c.StartY == 1

    with pytest.raises(NotImplementedError):
        c.SubExposureDuration
    with pytest.raises(NotImplementedError):
        c.SubExposureDuration = 1

    m.Connected = False


@pytest.skipif(platform.system() != "Windows", reason="Maxim only runs on Windows")
def test_maxim_filter_wheel():
    m = Maxim()
    f = m.filter_wheel
    f.Connected = True
    assert f.Connected

    assert f.Name is not None

    with pytest.raises(NotImplementedError):
        f.FocusOffsets

    assert f.Names is not None
    assert f.Position is not None
    f.Position = 1
    assert f.Position == 1

    m.Connected = False


@pytest.skipif(platform.system() != "Windows", reason="Maxim only runs on Windows")
def test_maxim_pinpoint():
    m = Maxim()
    p = m.pinpoint

    m.Camera.StartExposure(1, True)
    while not m.Camera.ImageReady:
        time.sleep(0.1)

    assert p.Solve() is not None

    m.Connected = False
