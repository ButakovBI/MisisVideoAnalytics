import pytest
from fastapi.testclient import TestClient
from source.main import app


@pytest.fixture
def client():
    return TestClient(app)
