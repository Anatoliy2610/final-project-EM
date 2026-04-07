from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_db
from app.core.exceptions import ExceptionService
from app.meetings.crud import MeetingCRUD


async def get_meeting_crud(db: AsyncSession = Depends(get_db)) -> MeetingCRUD:
    return MeetingCRUD(db)
