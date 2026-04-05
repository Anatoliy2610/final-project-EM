from sqlalchemy import select

from app.config import ALGORITHM, SECRET_KEY_TOKEN
from app.users.dependencies import get_db
from app.database import async_session_maker
from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from starlette.templating import Jinja2Templates
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from app.users.models import UserModel
from app.users.security import verify_password



async def authenticate_user(email: str, password: str, db: AsyncSession = Depends(get_db)):
    query = await db.scalars(select(UserModel).filter(UserModel.email == email))
    user = query.first()
    if (
        not user
        or verify_password(plain_password=password, hashed_password=user.hash_password)
        is False
    ):
        return None
    return user


def get_auth_data():
    return {"secret_key": SECRET_KEY_TOKEN, "algorithm": ALGORITHM}

