import pytest


class TestTaskClientAPI:

    @pytest.mark.asyncio
    async def test_get_tasks(self, setup_test_db, client, db_session, login_user):
        response = client.get("/tasks")
        assert response.status_code == 200

    @pytest.mark.asyncio
    def test_get_add_task(self, client, db_session, login_user):
        response = client.get("/add_task")
        assert response.status_code == 200

    @pytest.mark.asyncio
    def test_add_task(self, client, db_session, login_user):
        client.post("/add_team", json={"name": "team for task"})
        response = client.post("/add_task", json={
            'name': 'task_1',
            'executor_id': 1,
            'dedline': '2026-04-15',
            'description': 'Описание задачи'
        })
        assert response.status_code == 200
        response = client.post("/add_task", json={
            'name': 'task_1',
            'executor_id': 10,
            'dedline': '2026-04-15',
            'description': 'Описание задачи'
        })
        assert response.status_code == 404

    @pytest.mark.asyncio
    def test_update_task(self, client, db_session, login_user):
        response = client.patch("/update_task", json={
            'id': 1,
            'new_name': 'New nama task 1',
            'executor_id': 2,
            'status': 'в работе',
            'dedline': '2026-04-25',
            'description': 'Новое Описание задачи'
        })
        assert response.status_code == 200

    @pytest.mark.asyncio
    def test_job_evaluation(self, client, db_session, login_user):
        response = client.get("/job_evaluation/1")
        assert response.status_code == 200
        response = client.patch("/job_evaluation", json={
            'id': 2,
            'name': 'task_1',
            'job_evaluation': 6
        })
        assert response.status_code == 404

    @pytest.mark.asyncio
    def test_add_message_chat(self, client, db_session, login_user):
        response = client.post("/add_message", json={
            "task_id": 1,
            "message": 'message for task 1'
        })
        assert response.status_code == 200

    @pytest.mark.asyncio
    def test_get_task_user(self, client, db_session, login_user):
        response = client.get('/task_user/1')
        assert response.status_code == 200
        # удаляем себя из команды
        client.patch('/delete_user_to_team', json={'email_user': 'test@example.com'})
