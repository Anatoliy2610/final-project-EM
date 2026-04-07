from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import logger
from app.meetings.models import MeetingModel
from app.users.models import UserModel


class MeetingCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_meetings_db(self, user_data):
        try:
            query = await self.db.execute(
                select(MeetingModel)
                .filter(MeetingModel.team_id == user_data.team_id)
                .options(
                    selectinload(MeetingModel.team),
                    selectinload(MeetingModel.participants),
                )
            )
            return query.scalars().all()
        except DatabaseError as e:
            logger.error(f"Ошибка БД при получении встреч: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка при получении данных о встречах"
            )

    async def get_team_users_db(self, user_data):
        try:
            query = await self.db.execute(
                select(UserModel).filter(UserModel.team_id == user_data.team_id)
            )
            return query.scalars().all()
        except DatabaseError as e:
            logger.error(f"Ошибка БД при получении пользователей команды: {e}")
            raise HTTPException(
                status_code=500,
                detail="Ошибка при получении данных о пользователях команды",
            )

    async def add_meeting_db(self, user_data, data_meeting):
        try:
            query_participants = await self.db.execute(
                select(UserModel).filter(
                    UserModel.id.in_(data_meeting.participants),
                    UserModel.team_id == user_data.team_id,
                )
            )
            participants = query_participants.scalars().all()
            db_meeting = MeetingModel(
                name=data_meeting.name,
                datetime_beginning=data_meeting.datetime_beginning,
                datetime_end=data_meeting.datetime_beginning + timedelta(hours=1),
                team_id=user_data.team_id,
            )
            db_meeting.participants = participants
            self.db.add(db_meeting)
            await self.db.commit()
            await self.db.refresh(db_meeting)
            return db_meeting

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании встречи: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось создать встречу из‑за конфликта данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при создании встречи: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при создании встречи"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при создании встречи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при создании встречи",
            )

    async def delete_meeting_db(self, data_meeting):
        try:
            query = await self.db.execute(
                select(MeetingModel).filter(MeetingModel.id == data_meeting.id)
            )
            meeting = query.scalars().first()

            if not meeting:
                raise HTTPException(status_code=404, detail="Встреча не найдена")

            await self.db.delete(meeting)
            await self.db.commit()

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при удалении встречи: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось удалить встречу из‑за связанных данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при удалении встречи: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при удалении встречи"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при удалении встречи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при удалении встречи",
            )

    async def get_meetings_user_db(self, user_id):
        try:
            query = await self.db.execute(
                select(UserModel)
                .filter(UserModel.id == user_id)
                .options(selectinload(UserModel.meetings))
            )
            return query.scalars().first()
        except DatabaseError as e:
            logger.error(f"Ошибка БД при получении встреч пользователя: {e}")
            raise HTTPException(
                status_code=500,
                detail="Ошибка при получении данных о встречах пользователя",
            )
