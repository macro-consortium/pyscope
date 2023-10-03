import pytest


def test_sensordescription(winer_oc):
    assert winer_oc.SensorDescription("rain_rate") == "RAIN"


def test_timesincelastupdate(winer_oc):
    assert winer_oc.TimeSinceLastUpdate("rain_rate") is not None


def test_averageperiod(winer_oc):
    assert winer_oc.AveragePeriod is None
    winer_oc.AveragePeriod = 10  # Note for this driver this does nothing
    assert winer_oc.AveragePeriod is None


def test_cloudcover(winer_oc):
    winer_oc.CloudCover is None


def test_dewpoint(winer_oc):
    winer_oc.DewPoint is None


def test_humidity(winer_oc):
    winer_oc.Humidity is not None


def test_pressure(winer_oc):
    winer_oc.Pressure is not None


def test_rainrate(winer_oc):
    winer_oc.RainRate is not None


def test_skybrightness(winer_oc):
    winer_oc.SkyBrightness is not None


def test_skyquality(winer_oc):
    winer_oc.SkyQuality is None


def test_skytemperature(winer_oc):
    winer_oc.SkyTemperature is None


def test_starfwhm(winer_oc):
    winer_oc.StarFWHM is not None


def test_temperature(winer_oc):
    winer_oc.Temperature is not None


def test_winddirection(winer_oc):
    winer_oc.WindDirection is not None


def test_windgust(winer_oc):
    winer_oc.WindGust is None


def test_windspeed(winer_oc):
    winer_oc.WindSpeed is not None
