from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_db
from app.users.auth import get_auth_data
from app.users.crud import UserCRUD
from app.users.models import UserModel


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> UserModel:
    """
    Извлекает и валидирует текущего пользователя из cookie-файла "access_token".
    """
    access_token = request.cookies.get("access_token")
    if not access_token:
        return None
    try:
        auth_config = await get_auth_data()
        payload = jwt.decode(
            access_token,
            auth_config["secret_key"],
            algorithms=[auth_config["algorithm"]],
        )
        expire_timestamp = payload.get("exp")
        if expire_timestamp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен (нет exp)",
            )
        expire_time = datetime.fromtimestamp(int(expire_timestamp), tz=timezone.utc)
        # Проверяем, не истек ли срок действия токена
        if expire_time < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Срок действия токена истек",
            )
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен (нет sub)",
            )
        query = await db.scalars(
            select(UserModel)
            .filter(UserModel.id == int(user_id_str))
            .options(
                selectinload(UserModel.team),
                selectinload(UserModel.meetings),
                selectinload(UserModel.tasks),
            )
        )
        user = query.first()
        if user is None:
            return None
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка при проверке токена",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат ID пользователя в токене",
        )
    except Exception as e:
        print(f"Неожиданная ошибка в get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при аутентификации",
        )


async def get_user_crud(db: AsyncSession = Depends(get_db)) -> UserCRUD:
    return UserCRUD(db)
