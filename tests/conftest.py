from typing import List

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.core.config import get_db
from app.core.database import Base
from app.meetings.models import MeetingModel
from app.tasks.models import TaskModel
from app.teams.models import TeamModel
from app.users.models import UserModel


from fastapi import FastAPI
from sqladmin import Admin

from app.admin.admin_views import MeetingAdmin, TaskAdmin, TeamAdmin, UserAdmin
from app.calendar.router import router as calendar
from app.core.database import Base, async_engine
from app.meetings.router import router as meeting_router
from app.tasks.router import router as task_router
from app.teams.router import router as team_router
from app.users.router import router as user_router

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine



TEST_SQL_BD_URL = "sqlite+aiosqlite:///./test.db"

test_async_engine = create_async_engine(TEST_SQL_BD_URL, echo=True, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(test_async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
async def setup_test_db():
    """Создаёт тестовую БД перед тестами и удаляет после"""
    # Создаём все таблицы
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # Здесь выполняются тесты 
    # Удаляем тестовую БД после завершения тестов
    await test_async_engine.dispose()
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture(scope="function")
async def db_session():
    """Предоставляет сессию БД для каждого теста"""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Клиент для тестирования API с подменой зависимости БД"""
    
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def login_user(client):
    create_user = client.post(
        "/register/",
        json={
            "email": "test@example.com",
            "password": "securepassword123"
        }
    )
    login = client.post('/login', json={
        "email": "test@example.com",
        "password": "securepassword123"
        })
    yield
