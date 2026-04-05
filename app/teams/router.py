from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from app.config import get_db, templates

from app.teams.crud import get_team_db, add_team_db, update_data_user_db
from app.users.dependencies import get_current_user
from app.teams.models import TeamModel
from app.teams.schemas import DeleteUserSChema, TeamSchema, UserTeamSchema
from app.teams.utils import (
                             check_absence_user, check_availability_team,
                             check_user_absence_role, check_user_admin,
                             check_user_to_team, 
                             )
from app.users.models import UserModel
from app.users.schemas import User
from sqlalchemy import select


router = APIRouter(tags=["Команда"])


@router.get("/teams", response_model=List[TeamSchema])
async def get_teams(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    #
    query = await db.scalars(select(TeamModel))
    teams_data = query.all()
    #
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
        request,
        "teams/add_team.html", 
        {"request": request, "current_user": user_data}
    )


@router.post("/add_team")
async def add_teams(
    data_team: TeamSchema,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await add_team_db(data_team, user_data, db)
    return {"message": f"Команда зарегистрирована!"}


@router.get("/user_to_team")
async def get_add_or_update_user_to_team(
    request: Request, 
    user_data: UserModel = Depends(get_current_user)
):
    return templates.TemplateResponse(
        request, "teams/add_user_to_team.html", {"request": request, "current_user": user_data}
    )


@router.patch("/user_to_team")
async def add_or_update_user_to_team(
    data_user: UserTeamSchema,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_user_admin(user_data.role)
    query = await db.scalars(select(UserModel).filter(UserModel.email == data_user.email_user))
    user = query.first()
    check_absence_user(user)
    if user.role:
        check_user_to_team(user_admin=user, user_data=user_data)
        await update_user_to_team_db(user=user, new_role=data_user.role, db=db)
        return {
            "message": f"Пользователь {user.email} команды {user_data.team.name} получил новую роль {data_user.role}"
        }

    await add_user_to_team_db(user=user, admin_data=user_data, new_data_user=data_user, db=db)
    return {
        "message": f"Пользователь {user.email} добавлен в команду {user_data.team.name} с ролью {user.role}"
    }


@router.get("/team", response_model=List[User])
async def get_team(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = await db.execute(select(UserModel).filter(UserModel.team_id == user_data.team_id).options(selectinload(UserModel.team)))
    team = query.scalars().all()
    return templates.TemplateResponse(
        request, "teams/team.html", {"request": request, "current_user": user_data, "team": team}
    )


@router.patch("/delete_user_to_team")
async def delete_user_team(
    data_user: DeleteUserSChema,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_user_admin(user_data.role)
    query = await db.scalars(select(UserModel).filter(UserModel.email == data_user.email_user))
    user = query.first()
    check_absence_user(user)
    check_user_to_team(user_admin=user_data, user_data=user)
    user.role = None
    user.team_id = None
    await db.commit()
    return {"message": f"Пользователь {data_user.email_user} удален из команды"}
