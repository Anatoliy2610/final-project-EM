# from datetime import timedelta

# from fastapi import HTTPException, status

# from app.meetings.models import MeetingModel


# async def check_user_admin(user_role):
#     if user_role != "админ команды":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="У Вас не достаточно прав"
#         )


# async def check_meeting(meeting):
#     if meeting:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="На это время уже запланирована встреча",
#         )


# async def check_participants(participants, user_data):
#     for participant in participants:
#         if participant.team_id != user_data.team_id:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail="Есть участники, которые не состоят в вашей команде",
#             )


# async def check_not_meeting(meeting):
#     if not meeting:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Указанная встреча не найдена"
#         )
