import pytest


def test_sensordescription(device, disconnect):
    assert device.SensorDescription("CloudCover") is not None
    assert device.SensorDescription("DewPoint") is not None
    assert device.SensorDescription("Humidity") is not None
    assert device.SensorDescription("Pressure") is not None
    assert device.SensorDescription("RainRate") is not None
    assert device.SensorDescription("SkyBrightness") is not None
    assert device.SensorDescription("SkyQuality") is not None
    assert device.SensorDescription("SkyTemperature") is not None
    assert device.SensorDescription("StarFWHM") is not None
    assert device.SensorDescription("Temperature") is not None
    assert device.SensorDescription("WindDirection") is not None
    assert device.SensorDescription("WindGust") is not None
    assert device.SensorDescription("WindSpeed") is not None


def test_timesincelastupdate(device, disconnect):
    device.Refresh()
    assert device.TimeSinceLastUpdate("CloudCover") is not None
    assert device.TimeSinceLastUpdate("DewPoint") is not None
    assert device.TimeSinceLastUpdate("Humidity") is not None
    assert device.TimeSinceLastUpdate("Pressure") is not None
    assert device.TimeSinceLastUpdate("RainRate") is not None
    assert device.TimeSinceLastUpdate("SkyBrightness") is not None
    assert device.TimeSinceLastUpdate("SkyQuality") is not None
    assert device.TimeSinceLastUpdate("SkyTemperature") is not None
    assert device.TimeSinceLastUpdate("StarFWHM") is not None
    assert device.TimeSinceLastUpdate("Temperature") is not None
    assert device.TimeSinceLastUpdate("WindDirection") is not None
    assert device.TimeSinceLastUpdate("WindGust") is not None
    assert device.TimeSinceLastUpdate("WindSpeed") is not None


def test_averageperiod(device, disconnect):
    assert device.AveragePeriod is not None


def test_cloudcover(device, disconnect):
    assert device.CloudCover is not None


def test_dewpoint(device, disconnect):
    assert device.DewPoint is not None


def test_humidity(device, disconnect):
    assert device.Humidity is not None


def test_pressure(device, disconnect):
    assert device.Pressure is not None


def test_rainrate(device, disconnect):
    assert device.RainRate is not None


def test_skybrightness(device, disconnect):
    assert device.SkyBrightness is not None


def test_skyquality(device, disconnect):
    assert device.SkyQuality is not None


def test_skytemperature(device, disconnect):
    assert device.SkyTemperature is not None


def test_starfwhm(device, disconnect):
    assert device.StarFWHM is not None


def test_temperature(device, disconnect):
    assert device.Temperature is not None


def test_winddirection(device, disconnect):
    assert device.WindDirection is not None


def test_windgust(device, disconnect):
    assert device.WindGust is not None


def test_windspeed(device, disconnect):
    assert device.WindSpeed is not None
