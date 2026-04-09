# import os

import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

# SQL_BD_URL = os.getenv("SQL_BD_URL")
# SQL_BD_URL = "postgresql+asyncpg://postgres:password@db:5432/postgres"
SQL_BD_URL = "sqlite+aiosqlite:///./database.db"
TEST_SQL_BD_URL = "sqlite+aiosqlite:///./test.db"

if "TESTING" in os.environ:
    DATABASE_URL = TEST_SQL_BD_URL
else:
    DATABASE_URL = SQL_BD_URL

async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()
