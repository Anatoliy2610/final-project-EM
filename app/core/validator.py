from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.exceptions import ExceptionService
from app.core.config import get_db

async def get_validator(db: AsyncSession = Depends(get_db)) -> ExceptionService:
    return ExceptionService(db)