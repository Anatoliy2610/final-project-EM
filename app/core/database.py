# import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

# SQL_BD_URL = os.getenv("SQL_BD_URL")
SQL_BD_URL = "postgresql+asyncpg://postgres:password@db:5432/postgres"


async_engine = create_async_engine(SQL_BD_URL, echo=True)
async_session_maker = async_sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()
