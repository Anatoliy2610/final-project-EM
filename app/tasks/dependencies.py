from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_db
from app.tasks.crud import TaskCRUD


async def get_task_crud(db: AsyncSession = Depends(get_db)) -> TaskCRUD:
    return TaskCRUD(db)