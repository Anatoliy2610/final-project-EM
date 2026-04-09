from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from sqladmin import Admin

from app.admin.admin_views import MeetingAdmin, TaskAdmin, TeamAdmin, UserAdmin
from app.calendar.router import router as calendar
from app.core.database import Base, async_engine
from app.meetings.router import router as meeting_router
from app.tasks.router import router as task_router
from app.teams.router import router as team_router
from app.users.router import router as user_router


@asynccontextmanager
async def init_models(app: FastAPI):
    # Инициализация БД (только для продакшена)
    if "TESTING" not in os.environ:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield



app = FastAPI(lifespan=init_models)

admin = Admin(app, async_engine)
admin.add_view(UserAdmin)
admin.add_view(TaskAdmin)
admin.add_view(TeamAdmin)
admin.add_view(MeetingAdmin)

app.include_router(user_router)
app.include_router(team_router)
app.include_router(task_router)
app.include_router(meeting_router)
app.include_router(calendar)
