from typing import List
from fastapi import (APIRouter, Depends, Form, Request, Response)
from fastapi.responses import HTMLResponse

from app.core.exceptions import ExceptionService
from app.core.validator import get_validator
from app.users.crud import UserCRUD
from app.users.dependencies import get_current_user, get_user_crud
from app.users.models import UserModel
from app.users.schemas import UpdateUser, User, UserAuth, UserCreate
from app.core.config import templates

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
    user_crud: UserCRUD = Depends(get_user_crud)
):
    users_data = await user_crud.get_users_data()
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
async def register_user(
    user_data: UserCreate, 
    user_crud: UserCRUD = Depends(get_user_crud),
    validator: ExceptionService = Depends(get_validator),
    ):
    await validator.check_user(user_data=user_data)
    await user_crud.add_db(user_data=user_data)
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
    user_data: UserAuth, 
    user_crud: UserCRUD = Depends(get_user_crud),
    validator: ExceptionService = Depends(get_validator),
):
    await validator.check_data_login(user_data=user_data)
    response = await user_crud.authenticate_user(user_data=user_data)
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
    user_crud: UserCRUD = Depends(get_user_crud),
):
    await user_crud.update_db(user=current_user, data_user=data_user)
    return {"message": "Пользователь успешно изменен"}


@router.delete("/delete_user")
async def delete_user(
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    user_crud: UserCRUD = Depends(get_user_crud),
):
    await user_crud.delete_db(user=current_user, response=response)
    return {"message": "Пользователь успешно удален"}
