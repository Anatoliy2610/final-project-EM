from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, selectinload

from app.config import get_db, templates
from app.users.dependencies import get_current_user

from app.meetings.models import MeetingModel
from app.meetings.schemas import (MeetinAddSchema, MeetingSchema,
                                  MeetingSchemaDelete)
from app.meetings.utils import (add_meeting_db, check_meeting,
                                check_not_meeting, check_participants,
                                check_user_admin, delete_meeting_db)
from app.users.models import UserModel

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(tags=["Встречи"])


@router.get("/meetings", response_model=List[MeetingSchema])
async def get_meetings(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = await db.execute(select(MeetingModel).filter(
        MeetingModel.team_id == user_data.team_id)
        .options(
            # selectinload(MeetingModel.participants).joinedload(UserModel.email),
            selectinload(MeetingModel.team),
            selectinload(MeetingModel.participants)
            )
        )
    meetings_data = query.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="meetings/meetings.html",
        context={"meetings_data": meetings_data, "current_user": user_data},
    )


@router.get("/add_meeting")
async def get_add_meeting(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = await db.scalars(select(UserModel).filter(UserModel.team_id == user_data.team_id))
    team_users = query.all()
    return templates.TemplateResponse(
        request,
        "meetings/add_meeting.html",
        {"request": request, "current_user": user_data, "team_users": team_users},
    )


@router.post("/add_meeting")
async def add_meeting(
    data_meeting: MeetinAddSchema,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    check_user_admin(user_role=user_data.role)
    query_meeting = await db.scalars(select(MeetingModel).filter(
        MeetingModel.datetime_beginning <= data_meeting.datetime_beginning,
        data_meeting.datetime_beginning <= MeetingModel.datetime_end,
    ))
    meeting = query_meeting.first()
    check_meeting(meeting=meeting)
    query_participants = await db.scalars(select(UserModel).filter(
                UserModel.id.in_(data_meeting.participants),
                UserModel.team_id == user_data.team_id,
    ))
    participants = query_participants.all()
    check_participants(participants=participants, user_data=user_data)
    await add_meeting_db(
        data_meeting=data_meeting, user_data=user_data, participants=participants, db=db
    )
    return {"message": f"Назначена встреча в {data_meeting.datetime_beginning}"}


@router.delete("/delete_meeting")
async def delete_meeting(
    data_meeting: MeetingSchemaDelete,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_user_admin(user_role=user_data.role)
    query = await db.scalars(select(MeetingModel).filter(MeetingModel.id == data_meeting.id))
    meeting = query.first()
    check_not_meeting(meeting=meeting)
    await delete_meeting_db(meeting=meeting, db=db)
    return {
        "message": f"Удалена встреча '{meeting.name}' начало в {meeting.datetime_beginning}"
    }


@router.get("/meetings_user/{user_id}", response_model=List[MeetingSchema])
async def get_meetings_user(
    request: Request,
    user_id: int,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = await db.scalars(select(UserModel).filter(UserModel.id == user_id).options(
        selectinload(UserModel.meetings)
    ))
    meetings = query.first()


    return templates.TemplateResponse(
        request,
        "meetings/meetings_user.html",
        {"current_user": user_data, "meetings": meetings.meetings},
    )
