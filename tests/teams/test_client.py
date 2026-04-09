import pytest


class TestTeamClientAPI:
    @pytest.mark.asyncio
    async def test_get_teams(self, setup_test_db, client, db_session, login_user):
        response = client.get("/teams")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_add_team(self, client, db_session, login_user):
        response = client.get("/add_team")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_add_teams(self, client, db_session, login_user):
        response = client.post("/add_team", json={"name": "team1"})
        assert response.status_code == 200
        response = client.post("/add_team", json={"name": "team1"})
        assert response.status_code == 400
  
    @pytest.mark.asyncio
    async def test_get_add_user_to_team(self, client, db_session, login_user):
        response = client.get("/add_user_to_team")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_add_user_to_team(self, client, db_session, login_user, create_user):
        response = client.patch("/add_user_to_team", json={'email_user': 'TestUser1@mail.ru', 'role': 'сотрудник'})
        assert response.status_code == 200
        response = client.patch("/add_user_to_team", json={'email_user': 'TestUser1@mail.ru', 'role': 'менеджер'})
        assert response.status_code == 403
        response = client.patch("/add_user_to_team", json={'email_user': 'TestUser2@mail.ru', 'role': 'сотрудник'})
        assert response.status_code == 200
        response = client.patch("/add_user_to_team", json={'email_user': 'TestUser2@mail.ru', 'role': 'менеджер'})
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_update_user_to_team(self, client, db_session, login_user):
        response = client.get("/update_user_to_team")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_user_to_team(self, client, db_session, login_user):
        response = client.patch("/update_user_to_team", json={'email_user': 'TestUser1@mail.ru', 'role': 'менеджер'})
        assert response.status_code == 200
        response = client.patch("/update_user_to_team", json={'email_user': 'TestUser2@mail.ru', 'role': 'менеджер'})
        assert response.status_code == 200
        response = client.patch("/update_user_to_team", json={'email_user': 'TestUser1@mail.ru', 'role': 'error role'})
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_get_team(self, client, db_session, login_user):
        response = client.get('/team')
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_user_team(self, client, db_session, login_user):
        response = client.patch('/delete_user_to_team', json={'email_user': 'TestUser1@mail.ru'})
        assert response.status_code == 200
