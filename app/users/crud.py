



from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload


from app.users.models import UserModel
from app.users.security import create_access_token, get_password_hash
from app.users.utils import check_data_login, check_user


async def get_users_data(db):
    query = await db.execute(select(UserModel).options(selectinload(UserModel.team)))
    users_data = query.scalars().all()
    return users_data


async def add_db(user_data, db):
    query = await db.scalars(select(UserModel).filter(UserModel.email == user_data.email))
    user = query.first()
    check_user(user)
    db_user = UserModel(
        email=user_data.email, hash_password=get_password_hash(user_data.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)


async def get_response(user_data, db):
    query = await db.scalars(select(UserModel).filter(UserModel.email == user_data.email))
    user = query.first()
    check_data_login(user=user, user_data=user_data)
    access_token = create_access_token({"sub": str(user.id)})
    response = JSONResponse(
        content={"access_token": access_token, "refresh_token": None}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Защита от XSS
        samesite="lax",  # Защита от CSRF
    )
    return response


async def update_db(user, data_user, db):
    if data_user.email:
        user.email = data_user.email
    if data_user.password:
        user.hash_password = get_password_hash(data_user.password)
    await db.commit()


async def delete_db(user, response, db):
    await db.delete(user)
    await db.commit()
    response.delete_cookie(key="access_token")
