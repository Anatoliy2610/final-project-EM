from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.config import ALGORITHM, SECRET_KEY_TOKEN

from app.users.dependencies import get_db
from app.users.models import UserModel
from app.users.security import verify_password


async def authenticate_user(
    email: str, password: str, db: AsyncSession = Depends(get_db)
):
    query = await db.scalars(select(UserModel).filter(UserModel.email == email))
    user = query.first()
    if (
        not user
        or await verify_password(
            plain_password=password, hashed_password=user.hash_password
        )
        is False
    ):
        return None
    return user


async def get_auth_data():
    return {"secret_key": SECRET_KEY_TOKEN, "algorithm": ALGORITHM}
