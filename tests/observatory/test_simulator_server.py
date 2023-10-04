import pytest

from pyscope.observatory import SimulatorServer


@pytest.mark.skip(reason="pytest_sessionfinish should end server")
@pytest.mark.order("last")
def test_shutdown():
    del pytest.simulator_server
