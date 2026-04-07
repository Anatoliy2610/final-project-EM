from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_db
from app.core.exceptions import ExceptionService


async def get_validator(db: AsyncSession = Depends(get_db)) -> ExceptionService:
    return ExceptionService(db)
