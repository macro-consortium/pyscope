import pytest

from pyscope.observatory import SimulatorServer


@pytest.mark.order("last")
def test_shutdown():
    del pytest.simulator_server
