import pytest
from fastapi.testclient import TestClient
from misis_api.source.main import app


@pytest.fixture
def client():
    return TestClient(app)
