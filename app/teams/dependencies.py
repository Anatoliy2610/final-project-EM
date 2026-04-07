from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_db
from app.teams.crud import TeamCRUD


async def get_team_crud(db: AsyncSession = Depends(get_db)) -> TeamCRUD:
    return TeamCRUD(db)
