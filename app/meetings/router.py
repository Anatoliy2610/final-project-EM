from typing import List

from fastapi import APIRouter, Depends, Request


from app.core.config import templates
from app.core.exceptions import ExceptionService
from app.core.validator import get_validator
from app.meetings.crud import MeetingCRUD
from app.meetings.dependencies import get_meeting_crud
from app.users.dependencies import get_current_user


from app.meetings.schemas import (MeetinAddSchema, MeetingSchema,
                                  MeetingSchemaDelete)

from app.users.models import UserModel




router = APIRouter(tags=["Встречи"])


@router.get("/meetings", response_model=List[MeetingSchema])
async def get_meetings(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    meeting_crud: MeetingCRUD = Depends(get_meeting_crud)
):
    meetings_data = await meeting_crud.get_meetings_db(user_data=user_data)
    return templates.TemplateResponse(
        request=request,
        name="meetings/meetings.html",
        context={"meetings_data": meetings_data, "current_user": user_data},
    )


@router.get("/add_meeting")
async def get_add_meeting(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    meeting_crud: MeetingCRUD = Depends(get_meeting_crud)
):
    team_users = await meeting_crud.get_team_users_db(user_data=user_data)
    return templates.TemplateResponse(
        request,
        "meetings/add_meeting.html",
        {"request": request, "current_user": user_data, "team_users": team_users},
    )


@router.post("/add_meeting")
async def add_meeting(
    data_meeting: MeetinAddSchema,
    user_data: UserModel = Depends(get_current_user),
    meeting_crud: MeetingCRUD = Depends(get_meeting_crud),
    validator: ExceptionService = Depends(get_validator),
):
    await validator.check_user_admin(user_role=user_data.role)
    await validator.check_meeting(data_meeting=data_meeting)
    await meeting_crud.add_meeting_db(user_data=user_data, data_meeting=data_meeting)
    return {"message": f"Назначена встреча в {data_meeting.datetime_beginning}"}


@router.delete("/delete_meeting")
async def delete_meeting(
    data_meeting: MeetingSchemaDelete,
    user_data: UserModel = Depends(get_current_user),
    validator: ExceptionService = Depends(get_validator),
    meeting_crud: MeetingCRUD = Depends(get_meeting_crud)
):
    await validator.check_user_admin(user_role=user_data.role)
    await meeting_crud.delete_meeting_db(data_meeting=data_meeting)
    return {"message": "Встреча удалена"}


@router.get("/meetings_user/{user_id}", response_model=List[MeetingSchema])
async def get_meetings_user(
    request: Request,
    user_id: int,
    user_data: UserModel = Depends(get_current_user),
    meeting_crud: MeetingCRUD = Depends(get_meeting_crud)
):
    meetings = await meeting_crud.get_meetings_user_db(user_id=user_id)
    return templates.TemplateResponse(
        request,
        "meetings/meetings_user.html",
        {"current_user": user_data, "meetings": meetings.meetings},
    )
