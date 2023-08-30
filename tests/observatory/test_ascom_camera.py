import time

import pytest

from pyscope.observatory import ASCOMCamera


def test_connectivity(device, disconnect):
    assert device.Connected
    device.Connected = False
    assert not device.Connected
    device.Connected = True
    assert device.Connected


def test_description(device, disconnect):
    assert device.Description is not None


def test_driver_info(device, disconnect):
    assert device.DriverInfo is not None


def test_driver_version(device, disconnect):
    assert device.DriverVersion is not None


def test_interface_version(device, disconnect):
    assert device.InterfaceVersion is not None


def test_name(device, disconnect):
    assert device.Name is not None


def test_supported_actions(device, disconnect):
    assert device.SupportedActions is not None


def test_start_exposure(device, disconnect):
    device.StartExposure(1, True)
    time.sleep(2)
    assert device.ImageReady


def test_stop_exposure(device, disconnect):
    if device.CanStopExposure:
        device.StartExposure(1, True)
        device.StopExposure()


def test_abort_exposure(device, disconnect):
    if device.CanAbortExposure:
        device.StartExposure(1, True)
        device.AbortExposure()


"""def test_bayeroffsetx(device, disconnect):
    assert device.BayerOffsetX is not None

def test_bayeroffsety(device, disconnect):
    assert device.BayerOffsetY is not None"""


def test_binx(device, disconnect):
    assert device.BinX is not None
    device.BinX = 2
    assert device.BinX == 2


def test_biny(device, disconnect):
    assert device.BinY is not None
    device.BinY = 2
    assert device.BinY == 2


def test_camera_state(device, disconnect):
    assert device.CameraState is not None


def test_cameraxsize(device, disconnect):
    assert device.CameraXSize is not None


def test_cameraysize(device, disconnect):
    assert device.CameraYSize is not None


def test_canasymmetricbin(device, disconnect):
    assert device.CanAsymmetricBin is not None


def test_canfastreadout(device, disconnect):
    assert device.CanFastReadout is not None


"""def test_properties(device, settings, disconn):
    print(settings)
    assert device.CameraXSize == settings["CameraXSize"]
    assert device.CameraYSize == settings["CameraYSize"]
    assert device.CanAbortExposure == settings["CanAbortExposure"]
    assert device.CanAsymmetricBin == settings["CanAsymmetricBin"]
    assert device.CanFastReadout == settings["CanFastReadout"]
    assert device.CanGetCoolerPower == settings["CanGetCoolerPower"]
    assert device.CanPulseGuide == settings["CanPulseGuide"]
    assert device.CanSetCCDTemperature == settings["CanSetCCDTemperature"]
    assert device.ElectronsPerADU == settings["ElectronsPerADU"]
    assert device.ExposureMax == settings["MaxExposure"]
    assert device.ExposureMin == settings["MinExposure"]
    assert device.ExposureResolution == settings["ExposureResolution"]
    # assert device.FastReadout == settings['FastReadout']
    assert device.FullWellCapacity == settings["FullWellCapacity"]
    assert device.HasShutter == settings["HasShutter"]
    assert device.MaxADU == settings["MaxADU"]
    assert device.MaxBinX == settings["MaxBinX"]
    assert device.MaxBinY == settings["MaxBinY"]
    assert device.PixelSizeX == settings["PixelSizeX"]
    assert device.PixelSizeY == settings["PixelSizeY"]
    v = settings["ReadoutModes"]
    assert device.ReadoutModes == v.split(",")
    assert device.SensorName == settings["SensorName"]
    assert device.SensorType == SensorType(settings["SensorType"])


def test_cooler(device, settings, disconn):
    # assert settings["HasCooler"], "OmniSim Has Cooler must be ON"
    assert device.CanSetCCDTemperature, "OmniSim Can Set CCD Temperature must be ON"
    assert device.CanGetCoolerPower, "OmniSim Can Get Cooler Power must be ON"


@pytest.mark.skipif(
    (c_sets.get("GainMode", None) != 1 or c_sets.get("OffsetMode", None) != 1),
    reason='Requires OmniSim Gain and Offset modes to be "Gain Names"',
)
def test_named_gains_offsets(device, settings, disconn):
    v = settings["Gains"]
    assert device.Gains == v.split(","), "OmniSim must be set to Named Gains mode"
    device.Gain = 0
    assert device.Gain == 0
    v = settings["Offsets"]
    assert device.Offsets == v.split(","), 'OmniSim must be set to "Named Offsets" mode'
    device.Offset = 0
    assert device.Offset == 0


@pytest.mark.skipif(
    (c_sets.get("GainMode", None) != 1 or c_sets.get("OffsetMode", None) != 1),
    reason='Requires OmniSim Gain and Offset modes to be "Min Max"',
)
def test_min_max_gains_offsets(device, settings, disconn):
    assert (
        device.GainMin == settings["GainMin"]
    ), "OmniSim must be set to Max-Min Gains mode"
    assert device.GainMax == settings["GainMax"]
    tg = device.GainMin + (device.GainMax - device.GainMin) // 2
    device.Gain = tg
    assert device.Gain == tg
    assert (
        device.OffsetMin == settings["OffsetMin"]
    ), "OmniSim must be set to Max-Min Offsets mode"
    assert device.OffsetMax == settings["OffsetMax"]
    tg = device.OffsetMin + (device.OffsetMax - device.OffsetMin) // 2
    device.Offset = tg
    assert device.Offset == tg


@pytest.mark.skipif(
    (c_sets.get("GainMode", None) != 1 or c_sets.get("OffsetMode", None) != 1),
    reason='Requires OmniSim Gain and Offset modes to be "None"',
)
def test_disabled_gains_offsets(device, settings, disconn):
    with pytest.raises(
        NotImplementedException, match=".*Gain[^s].*"
    ):  # Assure exactly "Gain"
        v = device.Gain
    with pytest.raises(
        NotImplementedException, match=".*Offset[^s].*"
    ):  # Assure exactly "Offset"
        v = device.Offset
    with pytest.raises(NotImplementedException, match=".*GainMax.*"):
        v = device.GainMax
    with pytest.raises(
        NotImplementedException, match=".*GainMax.*"
    ):  # Sim (0.1.2) returns error for GainMax
        v = device.GainMin
    with pytest.raises(NotImplementedException, match=".*Gains.*"):
        v = device.Gains
    with pytest.raises(NotImplementedException, match=".*OffsetMax.*"):
        v = device.OffsetMax
    with pytest.raises(
        NotImplementedException, match=".*OffsetMax.*"
    ):  # Sim (0.1.2) returns error for OffsetMax
        v = device.OffsetMin
    with pytest.raises(NotImplementedException, match=".*Offsets.*"):
        v = device.Offsets


@pytest.mark.skipif(
    (c_sets.get("SensorType", None) == 0),
    reason="Requires OmniSim SensorType to be other than Monochrome",
)
def test_color_bayer(device, settings, disconn):
    assert device.BayerOffsetX == settings["BayerOffsetX"]
    assert device.BayerOffsetY == settings["BayerOffsetY"]


@pytest.mark.skipif(
    (c_sets.get("SensorType", None) == 0),
    reason="Requires OmniSim SensorType to be Monochrome",
)
def test_image_capture(device, settings, disconn):
    assert (
        device.CameraXSize != device.CameraYSize
    ), "Width must not be the same as height for test validity"
    assert device.MaxBinX >= 2, "Camera must support X binning >= 2"
    assert device.MaxBinY >= 2, "Camera must support Y binning >= 2"
    device.BinX = 2
    assert device.BinX == 2
    device.BinY = 2
    assert device.BinY == 2
    device.StartX = 0
    assert device.StartX == 0
    device.StartY = 0
    assert device.StartY == 0
    device.NumX = device.CameraXSize // device.BinX
    assert device.NumX == device.CameraXSize // device.BinX
    device.NumY = device.CameraYSize // device.BinY
    assert device.NumY == device.CameraYSize // device.BinY
    device.StartExposure(1.0, True)
    while not device.ImageReady:
        time.sleep(0.5)
    img = device.ImageArray
    assert len(img) == device.NumX
    assert len(img[0]) == device.NumY


def test_image_stop_abort(device, settings, disconn):
    assert device.MaxBinX >= 2, "OmniSim Camera must support X binning >= 2"
    assert device.MaxBinY >= 2, "OmniSim OmniSim Camera must support Y binning >= 2"
    assert device.CanAbortExposure, "OmniSim Can Abort Exposure must be ON"
    assert device.CanStopExposure, "OmniSim Can Stop Exposure must be ON"
    device.StartExposure(3, True)
    time.sleep(1)
    device.StopExposure
    while not device.ImageReady:
        time.sleep(0.1)
    device.StartExposure(3, True)
    time.sleep(1)
    device.AbortExposure
    while not device.ImageReady:
        time.sleep(0.1)"""
