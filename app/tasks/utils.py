from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select

from app.tasks.models import MessageModel, TaskModel


def check_user_admin(user_role):
    if user_role != "админ команды":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="У Вас не достаточно прав"
        )


def check_user(user):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователя не существует"
        )


def check_availability_task(task):
    if task:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Задача с таким названием для исполнителя существует",
        )


def check_absence_task(task):
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Такой задачи не существует"
        )


def check_executor(executor):
    if not executor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Исполнитель не в вашей команде",
        )


async def task_add_db(data_task, executor, db):
    db_task = TaskModel(
        name=data_task.name,
        executor_id=executor.id,
        status=data_task.status if data_task.status else "открыто",
        dedline=datetime(
            int(data_task.dedline.split("-")[0]),
            int(data_task.dedline.split("-")[1]),
            int(data_task.dedline.split("-")[2]),
        ),
        description=data_task.description,
        team_id=executor.team_id,
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)


async def task_update_db(data_task, db, task):
    if data_task.new_name:
        task.name = data_task.new_name
    if data_task.executor_id:
        task.executor_id = data_task.executor_id
    if data_task.status:
        task.status = data_task.status
    if data_task.dedline:
        task.dedline = datetime(
            int(data_task.dedline.split("-")[0]),
            int(data_task.dedline.split("-")[1]),
            int(data_task.dedline.split("-")[2]),
        )
    if data_task.description:
        task.description = data_task.description
    await db.commit()


async def task_delete_db(db, task):
    await db.delete(task)
    await db.commit()


async def add_evaluation_db(job_evaluation, task, db):
    if job_evaluation not in range(1, 6):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Оценка должны быть от 1 до 5"
        )
    task.job_evaluation = job_evaluation
    task.status = "выполнена"
    await db.commit()


async def add_message_db(data_chat, user_data, task, db):
    db_message = MessageModel(
        message=data_chat.message,
        sender_id=user_data.id,
        task_id=data_chat.task_id,
    )
    db_message.task = [task]
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)


def get_messages(task):
    result = ""
    if task:
        chat = task.chat
        for message in chat:
            if message:
                result += f"Сообщение '{message.message}' от пользователя с 'id {message.sender_id}' дата '{message.created_at}' | "
    return result


async def get_average_grade(task_id, db):
    query = await db.scalars(select(TaskModel).filter(
        TaskModel.executor_id == task_id,
        TaskModel.status == "выполнена"
    ))
    tasks_user = query.all()
    if tasks_user:
        res_sum = 0
        res_len = 0
        for task in tasks_user:
            res_sum += task.job_evaluation
            res_len += 1
        average_grade = res_sum / res_len
        return average_grade
    return 0
