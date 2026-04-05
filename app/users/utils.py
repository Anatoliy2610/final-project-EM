from fastapi import HTTPException
from starlette import status

from app.users.security import verify_password


def check_user(user):
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже существует"
        )


def check_data_login(user, user_data):
    if user is None or not verify_password(user_data.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
        )
