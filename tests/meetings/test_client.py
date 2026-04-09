import pytest


class TestMeetingClientAPI:
    @pytest.mark.asyncio
    async def test_get_meetings(self, setup_test_db, client, db_session, login_user):
        client.post("/add_team", json={"name": "team for task"})
        response = client.get("/meetings")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_add_meeting(self, client, db_session, login_user):
        response = client.get("/add_meeting")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_add_meeting(self, client, db_session, login_user):
        response = client.post("/add_meeting", json={
            'name': 'name meeting',
            'datetime_beginning': '2025-03-31',
            'participants': [1]
        })
        assert response.status_code == 200
        response = client.post("/add_meeting", json={
            'name': 'name meeting',
            'datetime_beginning': '2025-03-31',
            'participants': [1, 25, 30]
        })
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_get_meetings_user(self, client, db_session, login_user):
        response = client.get("/meetings_user/1")
        assert response.status_code == 200
