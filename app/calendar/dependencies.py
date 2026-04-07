from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.calendar.crud import CalendarCRUD
from app.core.config import get_db


async def get_calendar_crud(db: AsyncSession = Depends(get_db)) -> CalendarCRUD:
    return CalendarCRUD(db)
