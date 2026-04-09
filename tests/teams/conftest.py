import pytest


@pytest.fixture
def create_user(client):
    user1 = client.post("/register/",
        json={
            "email": "TestUser1@mail.ru",
            "password": "TestUser1@mail.ru"
        }
    )
    user2 = client.post("/register/",
        json={
            "email": "TestUser2@mail.ru",
            "password": "TestUser2@mail.ru"
        }
    )
    yield