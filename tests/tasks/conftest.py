# import pytest


# @pytest.fixture
# def create_user(client):
#     user1 = client.post("/register/",
#         json={
#             "email": "TestUserTask1@mail.ru",
#             "password": "TestUserTask1@mail.ru"
#         }
#     )
#     user2 = client.post("/register/",
#         json={
#             "email": "TestUserTask2@mail.ru",
#             "password": "TestUserTask2@mail.ru"
#         }
#     )
#     yield

# @pytest.fixture
# def login_user_for_team(client, create_user):
#     client.post(
#         "/register/",
#         json={
#             "email": "test@example.com",
#             "password": "securepassword123"
#         }
#     )
#     client.post('/login', json={
#         "email": "test@example.com",
#         "password": "securepassword123"
#         })
#     client.post("/add_team", json={"name": "team for task"})
#     client.patch("/add_user_to_team", json={'email_user': 'TestUserTask1@mail.ru', 'role': 'сотрудник'})
#     client.patch("/add_user_to_team", json={'email_user': 'TestUserTask2@mail.ru', 'role': 'менеджер'})


#     yield

