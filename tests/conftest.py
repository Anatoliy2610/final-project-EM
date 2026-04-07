import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import AsyncMock, patch
from app.main import app


# Фикстура для создания AsyncClient
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# Фикстура для мокирования зависимости get_current_user
@pytest.fixture
def mock_get_current_user():
    with patch("your_module.get_current_user") as mock:
        mock.return_value = {"id": 1, "email": "test@example.com", "role": "админ команды"}
        yield mock
