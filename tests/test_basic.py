"""
Basic tests for the OPC UA CNC server.
"""

import pytest
from server.config import ServerConfig
from server.simulation import CNCSim, MachineState


def test_server_config():
    """Test server configuration loading."""
    config = ServerConfig()
    assert config.server is not None
    assert 'name' in config.server
    assert 'endpoint' in config.server


def test_cnc_simulation():
    """Test CNC simulation basic functionality."""
    config = {'noise_factor': 0.05}
    sim = CNCSim(config)
    
    # Test initial state
    assert sim.data.state == MachineState.IDLE
    assert sim.data.spindle.speed == 0.0
    
    # Test update
    data = sim.update(1.0)
    assert data is not None
    assert data.timestamp is not None


@pytest.mark.asyncio
async def test_opcua_server_creation():
    """Test OPC UA server creation."""
    from server.opcua_server import CNCOPCUAServer
    
    config = ServerConfig()
    server = CNCOPCUAServer(config)
    
    assert server.config is not None
    assert server.simulator is not None
    assert server.server is not None


if __name__ == "__main__":
    # Run simple tests
    test_server_config()
    test_cnc_simulation()
    print("Basic tests passed!")
