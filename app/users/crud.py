from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import logger
from app.users.models import UserModel
from app.users.security import create_access_token, get_password_hash
from app.users.utils import get_response


class UserCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users_data(self):
        try:
            query = await self.db.execute(
                select(UserModel).options(selectinload(UserModel.team))
            )
            return query.scalars().all()
        except DatabaseError as e:
            logger.error(f"Ошибка БД при получении данных пользователей: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка при получении данных о пользователях"
            )

    async def add_db(self, user_data):
        try:
            db_user = UserModel(
                email=user_data.email,
                hash_password=await get_password_hash(user_data.password),
            )
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании пользователя: {e}")
            raise HTTPException(
                status_code=409, detail="Пользователь с таким email уже существует"
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при создании пользователя: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при создании пользователя"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при создании пользователя: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при создании пользователя",
            )

    async def authenticate_user(self, user_data):
        try:
            query = await self.db.scalars(
                select(UserModel).filter(UserModel.email == user_data.email)
            )
            user = query.first()
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            access_token = await create_access_token({"sub": str(user.id)})
            response = await get_response(access_token)
            return response
        except DatabaseError as e:
            logger.error(f"Ошибка БД при аутентификации пользователя: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при аутентификации"
            )
        except Exception as e:
            logger.critical(f"Критическая ошибка при аутентификации: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при аутентификации",
            )

    async def update_db(self, user, data_user):
        try:
            if data_user.email:
                user.email = data_user.email
            if data_user.password:
                user.hash_password = await get_password_hash(data_user.password)
            await self.db.commit()
            return user
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при обновлении пользователя: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось обновить пользователя из‑за конфликта данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при обновлении пользователя: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при обновлении пользователя"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при обновлении пользователя: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при обновлении пользователя",
            )

    async def delete_db(self, user, response):
        try:
            await self.db.delete(user)
            await self.db.commit()
            response.delete_cookie(key="access_token")
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при удалении пользователя: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось удалить пользователя из‑за связанных данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при удалении пользователя: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при удалении пользователя"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при удалении пользователя: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при удалении пользователя",
            )
