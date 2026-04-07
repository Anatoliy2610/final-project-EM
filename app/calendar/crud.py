from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.users.models import UserModel


class CalendarCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_db(self, user):
        query = await self.db.execute(
            select(UserModel)
            .filter(UserModel.email == user.email)
            .options(
                selectinload(UserModel.meetings),
                selectinload(UserModel.tasks),
                selectinload(UserModel.team),
            )
        )
        return query.scalars().first()
