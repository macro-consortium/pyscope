import time

from pyscope.observatory import ASCOMCamera, SimulatorServer


def test_camera():
    server = SimulatorServer()
    cam = ASCOMCamera("127.0.0.1:32323", alpaca=True)
    time.sleep(5)

    assert not cam.Connected
    cam.Connected = True
    assert cam.Connected

    cam.Connected = False
    assert not cam.Connected
    del server
