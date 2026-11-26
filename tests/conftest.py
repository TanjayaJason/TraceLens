import socket
import pytest

@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """No external network access is permitted in this suite."""
    def blocked(*args, **kwargs):
        raise AssertionError('Network calls are forbidden in offline tests')
    monkeypatch.setattr(socket.socket, 'connect', blocked)
    monkeypatch.setattr(socket.socket, 'connect_ex', blocked)
