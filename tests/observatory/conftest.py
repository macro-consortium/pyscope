import ast
import os
import platform
import sys
import time
import xml.etree.ElementTree as ET

import pytest

from pyscope import observatory

# Much of these tests are inspired by the tests in the alpyca repo
# found here: https://github.com/ASCOMInitiative/alpyca


def pytest_configure():
    pytest.simulator_server = observatory.SimulatorServer()
    time.sleep(12)


def pytest_sessionfinish(session, exitstatus):
    del pytest.simulator_server


@pytest.fixture()
def device(request):
    global d
    n = "ASCOM" + "".join(
        [s.capitalize() for s in request.module.__name__.split("_")[2:]]
    )
    c = getattr(observatory, n)  # Creates a device class by string name :-)
    d = c("localhost:32323", alpaca=True)  # Created an instance of the class
    #    d = c('[fe80::9927:65fc:e9e8:f33a%eth0]:32323', 0)  # RPi 4 Ethernet to Windows OmniSim IPv6
    d.Connected = True
    return d


@pytest.fixture()
def disconnect(request):
    global d
    yield
    d.Connected = False
    n = "ASCOM" + "".join(
        [s.capitalize() for s in request.module.__name__.split("_")[2:]]
    )


@pytest.fixture()
def winer_oc(request):
    global d
    d = observatory.HTMLObservingConditions(
        "https://winer.org/Site/Weather.php",
        rain_rate_keyword="RAIN",
        rain_rate_units="in",
        sky_brightness_keyword="BRIGHTNESS",
        sky_brightness_units="Vmag/sq.asec",
        star_fwhm_keyword="LAST_SEEING",
        star_fwhm_units='"',
        wind_direction_keyword="WINDDIR",
    )
    return d


"""@pytest.fixture()
def settings(request):
    n = request.module.__name__.split('_')[-1].capitalize()
    if platform.system() == "Windows":
        data_file = f"{os.getenv('USERPROFILE')}/.ASCOM/Alpaca/ASCOM-Alpaca-Simulator/{n}/v1/Instance-0.xml"
    else:                       # TODO No MacOS
        n = n.lower()
        data_file = f"{os.getenv('HOME')}/.config/ascom/alpaca/ascom-alpaca-simulator/{n}/v1/instance-0.xml"
    tree = ET.parse(data_file)
    root = tree.getroot()
    s = {}
    for i in root.iter("SettingsPair"):
        k = i.find('Key').text
        v = i.find('Value').text
        try:
            s[k] = ast.literal_eval(v)
        except:
            s[k] = v
    return s

def get_settings(device):
    if platform.system() == "Windows":
        data_file = f"{os.getenv('USERPROFILE')}/.ASCOM/Alpaca/ASCOM-Alpaca-Simulator/{device}/v1/Instance-0.xml"
    else:                       # TODO No MacOS
        device = device.lower()
        data_file = f"{os.getenv('HOME')}/.config/ascom/alpaca/ascom-alpaca-simulator/{device}/v1/instance-0.xml"
    tree = ET.parse(data_file)
    root = tree.getroot()
    s = {}
    for i in root.iter("SettingsPair"):
        k = i.find('Key').text
        v = i.find('Value').text
        try:
            s[k] = ast.literal_eval(v)
        except:
            s[k] = v
    return s"""
