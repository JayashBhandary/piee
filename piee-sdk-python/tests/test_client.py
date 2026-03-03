import pytest
from piee import PIEE

def test_piee_init():
    # Test default initialization
    client = PIEE(api_key="pk-test")
    assert client._http_client.base_url == "https://api.piee.app"
    assert client._http_client.headers["X-API-Key"] == "pk-test"
    
def test_piee_local_init():
    # Test local initialization
    client = PIEE(base_url="http://localhost:8000", api_key="test-key")
    assert client._http_client.base_url == "http://localhost:8000"
    assert client._http_client.headers["Authorization"] == "Bearer test-key"

def test_piee_namespaces():
    client = PIEE()
    assert hasattr(client, "chat")
    assert hasattr(client.chat, "completions")
    assert hasattr(client, "embeddings")
    assert hasattr(client, "models")
    assert hasattr(client, "auth")
    assert hasattr(client, "billing")
    assert hasattr(client, "usage")
