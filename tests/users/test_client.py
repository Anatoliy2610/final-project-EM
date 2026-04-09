import pytest


class TestUserClientAPI:
    @pytest.mark.asyncio
    async def test_index(self, client):
        response = client.get('/')
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_users(self, client, db_session):
        response = client.get('/users')
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_register_user(self, client, db_session):
        response = client.post(
            "/register/",
            json={
                "email": "test_user@mail.ru",
                "password": "test_user@mail.ru"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Вы успешно зарегистрированы!"

        response = client.post(
            "/register/",
            json={
                "email": "test_user@mail.ru",
                "password": "test_user@mail.ru"
            }
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_auth_user(self, client, db_session):
        response = client.post('/login', json={
            "email": "test_user@mail.ru",
            "password": "test_user@mail.ru"
            })
        assert response.status_code == 200
        response = client.post('/login', json={
            "email": "ErrorEmail@mail.ru",
            "password": "Error-password"
            })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_user(self, client, db_session, login_user):
        response = client.get('/user')
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_user(self, client, db_session, login_user):
        response = client.get('/update_user')
        assert response.status_code == 200
        response = client.patch('/update_user', json={'email': 'User1@mail.ru', 'password': 'password'})
        assert response.status_code == 200
        response = client.patch('/update_user', json={'email': 'test@example.com', 'password': 'securepassword123'})
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_delete_user(self, client, db_session, login_user):
        response = client.delete('/delete_user')
        assert response.status_code == 200
