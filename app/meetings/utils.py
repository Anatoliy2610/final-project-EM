from datetime import timedelta

from fastapi import HTTPException, status

from app.meetings.models import MeetingModel


def check_user_admin(user_role):
    if user_role != "админ команды":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="У Вас не достаточно прав"
        )


def check_meeting(meeting):
    if meeting:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="На это время уже запланирована встреча",
        )


def check_participants(participants, user_data):
    for participant in participants:
        if participant.team_id != user_data.team_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Есть участники, которые не состоят в вашей команде",
            )


async def add_meeting_db(data_meeting, user_data, participants, db):
    db_meeting = MeetingModel(
        name=data_meeting.name,
        datetime_beginning=data_meeting.datetime_beginning,
        datetime_end=data_meeting.datetime_beginning + timedelta(hours=1),
        team_id=user_data.team_id,
    )
    db_meeting.participants = participants
    db.add(db_meeting)
    await db.commit()
    await db.refresh(db_meeting)


def check_not_meeting(meeting):
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Указанная встреча не найдена"
        )


async def delete_meeting_db(meeting, db):
    await db.delete(meeting)
    await db.commit()
