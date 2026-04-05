from typing import List

from fastapi import (APIRouter, Depends, Form, HTTPException, Request,
                     Response, status)
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session, selectinload


from app.users.crud import add_db, delete_db, get_response, get_users_data, update_db
from app.users.dependencies import get_current_user
from app.users.models import UserModel
from app.users.schemas import UpdateUser, User, UserAuth, UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_db, templates

router = APIRouter(tags=["Пользователь"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, current_user: UserModel = Depends(get_current_user)):
    return templates.TemplateResponse(
        request=request, 
        name="base.html", 
        context={"current_user": current_user}
    )


@router.get("/users", response_model=List[User])
async def get_users(
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    users_data = await get_users_data(db=db)
    return templates.TemplateResponse(
        request=request,
        name="users/users.html",
        context={"users_data": users_data, "current_user": current_user},
    )


@router.get("/register-form/", response_class=HTMLResponse)
async def show_register_form(
    request: Request, current_user: UserModel = Depends(get_current_user)
):
    return templates.TemplateResponse(
        request=request,
        name="users/register.html", 
        context={"request": request, "current_user": current_user}
    )


@router.post("/register/")
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    await add_db(user_data=user_data, db=db)
    return {"message": "Вы успешно зарегистрированы!"}


@router.get("/login-form/", response_class=HTMLResponse)
async def show_login_form(
    request: Request, current_user: UserModel = Depends(get_current_user)
):
    return templates.TemplateResponse(
        request=request,
        name="users/login.html", 
        context={"request": request, "current_user": current_user}
    )


@router.post("/login/")
async def auth_user(
    user_data: UserAuth, response: Response, db: AsyncSession = Depends(get_db)
):
    response = await get_response(user_data=user_data, db=db)
    return response


@router.post("/logout/")
async def logout_user(
    response: Response, current_user: UserModel = Depends(get_current_user)
):
    response.delete_cookie(key="access_token")
    return {"message": "Пользователь успешно вышел из системы"}


@router.get("/user", response_model=User)
async def get_user(
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    # db: AsyncSession = Depends(get_db),
):
    return templates.TemplateResponse(
        request=request,
        name="users/user.html",
        context={"current_user": current_user},
    )


@router.get("/update_user")
async def get_update_user(
    request: Request, current_user: UserModel = Depends(get_current_user)
):
    return templates.TemplateResponse(
        request, "users/update_user.html", {"request": request, "current_user": current_user}
    )


@router.patch("/update_user")
async def update_user(
    data_user: UpdateUser,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await update_db(user=current_user, data_user=data_user, db=db)
    return {"message": "Пользователь успешно изменен"}


@router.delete("/delete_user")
async def delete_user(
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    delete_db(user=current_user, response=response, db=db)
    return {"message": "Пользователь успешно удален"}
