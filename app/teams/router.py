from typing import List

from fastapi import APIRouter, Depends, Request

from app.core.config import templates
from app.core.exceptions import ExceptionService
from app.core.validator import get_validator
from app.teams.crud import TeamCRUD
from app.teams.dependencies import get_team_crud
from app.teams.schemas import DeleteUserSChema, TeamSchema, UserTeamSchema
from app.users.dependencies import get_current_user
from app.users.models import UserModel
from app.users.schemas import User

router = APIRouter(tags=["Команда"])


@router.get("/teams", response_model=List[TeamSchema])
async def get_teams(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    team_crud: TeamCRUD = Depends(get_team_crud),
):
    teams_data = await team_crud.get_teams_db()
    return templates.TemplateResponse(
        request=request,
        name="teams/teams.html",
        context={"teams_data": teams_data, "current_user": user_data},
    )


@router.get("/add_team")
async def get_add_team(
    request: Request, user_data: UserModel = Depends(get_current_user)
):
    return templates.TemplateResponse(
        request, "teams/add_team.html", {"request": request, "current_user": user_data}
    )


@router.post("/add_team")
async def add_teams(
    data_team: TeamSchema,
    user_data: UserModel = Depends(get_current_user),
    validator: ExceptionService = Depends(get_validator),
    team_crud: TeamCRUD = Depends(get_team_crud),
):
    await validator.check_availability_team(data_team=data_team)
    await validator.check_user_absence_role(role=user_data.role)
    await team_crud.add_team_db(data_team, user_data)
    return {"message": "Команда зарегистрирована!"}


@router.get("/add_user_to_team")
async def get_add_user_to_team(
    request: Request,
    validator: ExceptionService = Depends(get_validator),
    user_data: UserModel = Depends(get_current_user),
):
    await validator.check_user_admin(user_role=user_data.role)
    return templates.TemplateResponse(
        request,
        "teams/add_user_to_team.html",
        {"request": request, "current_user": user_data},
    )


@router.patch("/add_user_to_team")
async def add_user_to_team(
    data_user: UserTeamSchema,
    user_data: UserModel = Depends(get_current_user),
    validator: ExceptionService = Depends(get_validator),
    team_crud: TeamCRUD = Depends(get_team_crud),
):
    await validator.check_user_admin(user_role=user_data.role)
    await validator.check_absence_user(data_user=data_user)
    await validator.check_role(role=data_user.role)
    await team_crud.add_user_db(user_data=user_data, new_user=data_user)
    return {
        "message": f"Пользователь {data_user.email_user} добавлен в команду {user_data.team.name} с ролью {data_user.role}"
    }


@router.get("/update_user_to_team")
async def get_update_user_to_team(
    request: Request,
    validator: ExceptionService = Depends(get_validator),
    user_data: UserModel = Depends(get_current_user),
):
    await validator.check_user_admin(user_role=user_data.role)
    return templates.TemplateResponse(
        request,
        "teams/update_user_to_team.html",
        {"request": request, "current_user": user_data},
    )


@router.patch("/update_user_to_team")
async def update_user_to_team(
    data_user: UserTeamSchema,
    user_data: UserModel = Depends(get_current_user),
    validator: ExceptionService = Depends(get_validator),
    team_crud: TeamCRUD = Depends(get_team_crud),
):
    await validator.check_user_admin(user_role=user_data.role)
    await validator.check_user_to_team(user=user_data, data_user=data_user)
    await validator.check_role(role=data_user.role)
    await team_crud.update_user_db(user=user_data, data_user=data_user)
    return {
        "message": f"Пользователь {data_user.email_user} команды {user_data.team.name} получил новую роль {data_user.role}"
    }


@router.get("/team", response_model=List[User])
async def get_team(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    team_crud: TeamCRUD = Depends(get_team_crud),
):
    team = await team_crud.get_team_db(user=user_data)
    return templates.TemplateResponse(
        request,
        "teams/team.html",
        {"request": request, "current_user": user_data, "team": team},
    )


@router.patch("/delete_user_to_team")
async def delete_user_team(
    data_user: DeleteUserSChema,
    user_data: UserModel = Depends(get_current_user),
    validator: ExceptionService = Depends(get_validator),
    team_crud: TeamCRUD = Depends(get_team_crud),
):
    await validator.check_user_admin(user_role=user_data.role)
    await team_crud.delete_user_db(user=user_data, user_data=data_user)
    return {"message": f"Пользователь {data_user.email_user} удален из команды"}
