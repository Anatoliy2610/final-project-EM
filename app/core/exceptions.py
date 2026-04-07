from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.meetings.models import MeetingModel
from app.tasks.models import TaskModel
from app.teams.models import TeamModel
from app.users.models import UserModel
from app.users.security import verify_password


class ExceptionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_user(self, user_data):
        query = await self.db.scalars(
            select(UserModel).filter(UserModel.email == user_data.email)
        )
        user = query.first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь уже существует",
            )

    async def check_data_login(self, user_data):
        query = await self.db.scalars(
            select(UserModel).filter(UserModel.email == user_data.email)
        )
        user = query.first()
        if user is None or not verify_password(user_data.password, user.hash_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль",
            )

    async def check_user_admin(self, user_role):
        if user_role != "админ команды":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="У Вас не достаточно прав"
            )

    async def check_meeting(self, data_meeting):
        query_meeting = await self.db.execute(
            select(MeetingModel).filter(
                MeetingModel.datetime_beginning <= data_meeting.datetime_beginning,
                data_meeting.datetime_beginning <= MeetingModel.datetime_end,
            )
        )
        meeting = query_meeting.scalars().first()
        if meeting:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="На это время уже запланирована встреча",
            )

    async def check_executor(self, data_task, user):
        query_executor = await self.db.execute(
            select(UserModel).filter(
                UserModel.id == data_task.executor_id,
                UserModel.team_id == user.team_id,
            )
        )
        executor = query_executor.scalars().first()
        if not executor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Исполнитель не в вашей команде",
            )

    async def check_availability_task(self, data_task):
        query_task = await self.db.execute(
            select(TaskModel).filter(
                TaskModel.name == data_task.name,
                TaskModel.executor_id == data_task.executor_id,
            )
        )
        task = query_task.first()
        if task:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Задача с таким названием для исполнителя существует",
            )

    async def check_absence_task(self, user, data_task):
        query = await self.db.execute(
            select(TaskModel).filter(
                TaskModel.id == data_task.id, TaskModel.team_id == user.team_id
            )
        )
        task = query.scalars().first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Такой задачи не существует",
            )

    async def check_job_evaluation(self, job_evaluation):
        if job_evaluation not in range(1, 6):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Оценка должны быть от 1 до 5",
            )

    async def check_availability_team(self, data_team):
        query = await self.db.execute(
            select(TeamModel).filter(TeamModel.name == data_team.name)
        )
        team = query.scalars().first()
        if team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Команда с таким названием уже существует",
            )

    async def check_user_absence_role(self, role):
        if role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы уже состоите в команде",
            )

    async def check_absence_user(self, data_user):
        query = await self.db.execute(
            select(UserModel).filter(UserModel.email == data_user.email_user)
        )
        user = query.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователя не существует",
            )
        if user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь состоит в команде",
            )

    async def check_role(self, role):
        if role not in ("менеджер", "сотрудник"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Такой роли не существует"
            )

    async def check_user_to_team(self, user, data_user):
        query = await self.db.execute(
            select(UserModel).filter(UserModel.email == data_user.email_user)
        )
        user = query.scalars().first()
        if user.team_id != data_user.team_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь не состоит в вашей команде",
            )
