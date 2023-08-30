import pytest

from pyscope.observatory import SimulatorServer


@pytest.mark.order(after="test_ascom_telescope")
def test_shutdown():
    del pytest.simulator_server
