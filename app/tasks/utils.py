from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select

from app.tasks.models import MessageModel, TaskModel


async def check_user_admin(user_role):
    if user_role != "админ команды":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="У Вас не достаточно прав"
        )


async def check_executor(executor):
    if not executor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Исполнитель не в вашей команде",
        )


async def check_availability_task(task):
    if task:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Задача с таким названием для исполнителя существует",
        )
    

async def check_absence_task(task):
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Такой задачи не существует"
        )


async def check_job_evaluation(job_evaluation):
    if job_evaluation not in range(1, 6):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Оценка должны быть от 1 до 5"
        )
