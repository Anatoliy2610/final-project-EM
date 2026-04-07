from fastapi import HTTPException
from httpx import patch
import pytest
from sqlalchemy.exc import DatabaseError

from app.core.exceptions import ExceptionService
from app.users.crud import UserCRUD
from app.users.schemas import UserCreate


@pytest.mark.asyncio
async def test_index_endpoint(async_client, mock_get_current_user):
    response = await async_client.get("/")
    assert response.status_code == 200
    # assert "text/html" in response.headers["content-type"]
    # Проверяем, что в ответе есть данные текущего пользователя
    # assert b"test@example.com" in response.content


# @pytest.mark.asyncio
# async def test_get_users_endpoint(async_client, mock_get_current_user):
#     # Мокируем метод get_users_data у UserCRUD
#     with patch.object(UserCRUD, "get_users_data") as mock_get_users:
#         # Создаём тестовые данные
#         test_users = [
#             {"id": 1, "email": "user1@example.com"},
#             {"id": 2, "email": "user2@example.com"}
#         ]
#         mock_get_users.return_value = test_users

#         response = await async_client.get("/users")

#         assert response.status_code == 200
#         assert "text/html" in response.headers["content-type"]
#         # Проверяем, что данные пользователей присутствуют в ответе
#         for user in test_users:
#             assert user["email"].encode() in response.content


# @pytest.mark.asyncio
# async def test_register_user_success(async_client, mock_get_current_user):
#     # Подготавливаем тестовые данные
#     user_data = UserCreate(email="newuser@example.com", password="securepassword")

#     # Мокируем зависимости
#     with patch.object(ExceptionService, "check_user") as mock_check_user, \
#          patch.object(UserCRUD, "add_db") as mock_add_db:
#         mock_check_user.return_value = None  # валидация прошла успешно
#         mock_add_db.return_value = None  # пользователь успешно добавлен

#         response = await async_client.post("/register/", json=user_data.dict())

#         # Проверяем статус и тип ответа
#         assert response.status_code == 200
#         assert response.headers["content-type"] == "application/json"

#         # Проверяем тело ответа
#         response_data = response.json()
#         assert response_data["message"] == "Вы успешно зарегистрированы!"



# @pytest.mark.asyncio
# async def test_register_user_validation_error(async_client, mock_get_current_user):
#     user_data = UserCreate(email="invalid-email", password="short")

#     with patch.object(ExceptionService, "check_user") as mock_check_user:
#         # Имитируем ошибку валидации
#         mock_check_user.side_effect = HTTPException(
#             status_code=400,
#             detail="Некорректный email"
#         )

#         response = await async_client.post("/register/", json=user_data.dict())

#         assert response.status_code == 400
#         response_data = response.json()
#         assert response_data["detail"] == "Некорректный email"


# @pytest.mark.asyncio
# async def test_register_user_database_error(async_client, mock_get_current_user):
#     user_data = UserCreate(email="user@example.com", password="password")

#     with patch.object(ExceptionService, "check_user") as mock_check_user, \
#          patch.object(UserCRUD, "add_db") as mock_add_db:
#         mock_check_user.return_value = None
#         # Имитируем ошибку БД
#         mock_add_db.side_effect = DatabaseError("DB error", None, None)

#         response = await async_client.post("/register/", json=user_data.dict())

#         assert response.status_code == 500
#         response_data = response.json()
#         assert "Ошибка базы данных" in response_data["detail"]


