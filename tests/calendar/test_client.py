import pytest

class TestCalendarClientAPI:
    @pytest.mark.asyncio
    async def test_get_user_calendar(self, setup_test_db, client, db_session, login_user):
        response = client.get("/meetings")
        assert response.status_code == 200
