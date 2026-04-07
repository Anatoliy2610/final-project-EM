from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import logger
from app.teams.models import TeamModel
from app.users.models import UserModel


class TeamCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_teams_db(self):
        query = await self.db.scalars(select(TeamModel))
        return query.all()

    async def get_team_db(self, user):
        query = await self.db.execute(
            select(UserModel)
            .filter(UserModel.team_id == user.team_id)
            .options(selectinload(UserModel.team))
        )
        return query.scalars().all()

    async def add_team_db(self, data_team, user):
        try:
            db_team = TeamModel(name=data_team.name)
            self.db.add(db_team)
            await self.db.commit()
            await self.db.refresh(db_team)
            user.team_id = db_team.id
            user.role = "админ команды"
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании задачи: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось создать задачу из‑за конфликта данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при создании задачи: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при создании задачи"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при создании задачи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при создании задачи",
            )

    async def add_user_db(self, user_data, new_user):
        try:
            query = await self.db.execute(
                select(UserModel).filter(UserModel.email == new_user.email_user)
            )
            user = query.scalars().first()
            user.role = new_user.role
            user.team_id = user_data.team_id
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании задачи: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось создать задачу из‑за конфликта данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при создании задачи: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при создании задачи"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при создании задачи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при создании задачи",
            )

    async def update_user_db(self, user, data_user):
        try:
            query = await self.db.scalars(
                select(UserModel).filter(UserModel.email == data_user.email_user)
            )
            user = query.first()
            user.role = data_user.role
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании задачи: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось создать задачу из‑за конфликта данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при создании задачи: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при создании задачи"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при создании задачи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при создании задачи",
            )

    async def delete_user_db(self, user, user_data):
        try:
            query = await self.db.scalars(
                select(UserModel).filter(UserModel.email == user_data.email_user)
            )
            user = query.first()
            user.role = None
            user.team_id = None
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании задачи: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось создать задачу из‑за конфликта данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при создании задачи: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при создании задачи"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при создании задачи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при создании задачи",
            )
