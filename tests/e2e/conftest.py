import pytest
from fastapi.testclient import TestClient

from src.entrypoint import app


@pytest.fixture
def test_client():
    with TestClient(app) as test_client:
        yield test_client
