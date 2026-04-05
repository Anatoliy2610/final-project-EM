from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, joinedload, selectinload

from app.config import get_db, templates
from app.users.dependencies import get_current_user
from app.tasks.models import MessageModel, TaskModel
from app.tasks.schemas import (EvaluationSchema, JobResultSchema,
                               MessageAddSchema, TaskAddSchema,
                               TaskDeleteSchema, TaskGetResponseSchema,
                               TaskUpdateSchema)
from app.tasks.utils import (add_evaluation_db, add_message_db,
                             check_absence_task, check_availability_task,
                             check_executor, check_user_admin,
                             get_average_grade, task_add_db, task_delete_db,
                             task_update_db)
from app.users.models import UserModel

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Задачи"])


@router.get("/tasks")
async def get_tasks(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = await db.execute(
        select(TaskModel).filter(TaskModel.team_id == user_data.team_id)
        .options(
            selectinload(TaskModel.executor),
            selectinload(TaskModel.team),
            selectinload(TaskModel.chat),
            ).order_by(TaskModel.id))
    data_tasks = query.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="tasks/tasks.html",
        context={"data_tasks": data_tasks, "current_user": user_data},
    )


@router.get("/add_task")
async def get_add_task(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = await db.scalars(select(UserModel).filter(UserModel.team_id == user_data.team_id))
    team_users = query.all()
    return templates.TemplateResponse(
        request=request,
        name="tasks/add_task.html",
        context={"request": request, "current_user": user_data, "team_users": team_users},
    )


@router.post("/add_task")
async def add_task(
    data_task: TaskAddSchema,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_user_admin(user_data.role)
    query_executor = await db.scalars(select(UserModel).filter(
        UserModel.id == data_task.executor_id,
        UserModel.team_id == user_data.team_id,
    ))
    executor = query_executor.first()
    check_executor(executor)
    query_task = await db.scalars(select(TaskModel).filter(
            TaskModel.name == data_task.name,
            TaskModel.executor_id == data_task.executor_id,
        ))
    task = query_task.first()
    check_availability_task(task)
    await task_add_db(data_task=data_task, executor=executor, db=db)
    return {"message": f"Задача зарегистрирована для {executor.email}"}


@router.post("/add_message")
async def add_message_chat(
    data_chat: MessageAddSchema,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query_task = await db.scalars(select(TaskModel).filter(
            TaskModel.id == data_chat.task_id, 
            TaskModel.team_id == user_data.team_id
        ))
    task = query_task.first()
    check_absence_task(task=task)
    await add_message_db(data_chat=data_chat, user_data=user_data, task=task, db=db)
    return {"message": f"Добавлено сообщение в чат к задаче {task.name}"}


@router.get("/update_task/{task_id}", response_model=TaskGetResponseSchema)
async def get_update_task(
    task_id: int,
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_user_admin(user_data.role)
    query_task = await db.scalars(select(TaskModel).filter(
            TaskModel.id == task_id,
            TaskModel.team_id == user_data.team_id
        ))
    task = query_task.first()
    query_team = await db.scalars(select(UserModel).filter(
            UserModel.team_id == user_data.team_id
        ))
    team_users = query_team.all()
    return templates.TemplateResponse(
        request,
        "tasks/update_task.html",
        {
            "request": request,
            "current_user": user_data,
            "task": task,
            "team_users": team_users,
        },
    )


@router.patch("/update_task")
async def update_task(
    data_task: TaskUpdateSchema,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_user_admin(user_data.role)
    query = await db.scalars(select(TaskModel).filter(
            TaskModel.id == data_task.id,
            TaskModel.team_id == user_data.team_id
        ))
    task = query.first()
    check_absence_task(task)
    await task_update_db(data_task=data_task, db=db, task=task)
    return {"message": f"Задача {data_task.id} изменена"}


@router.delete("/delete_task")
async def delete_task(
    data_task: TaskDeleteSchema,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_user_admin(user_data.role)
    query = await db.scalars(select(TaskModel).filter(
            TaskModel.id == data_task.id,
            TaskModel.executor_id == data_task.executor_id,
            TaskModel.team_id == user_data.team_id,
        ))
    task = query.first()
    check_absence_task(task)
    await task_delete_db(db=db, task=task)
    return {"message": f"Задача {task.name} удалена"}


@router.get("/job_evaluation/{task_id}", response_model=TaskGetResponseSchema)
async def get_job_evaluation(
    task_id: int,
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_user_admin(user_data.role)
    query = await db.scalars(select(TaskModel).filter(
            TaskModel.id == task_id, 
            TaskModel.team_id == user_data.team_id
        ).options(
            selectinload(TaskModel.executor)
        ))
    task = query.first()
    return templates.TemplateResponse(
        request,
        "tasks/job_evaluation.html",
        {"request": request, "current_user": user_data, "task": task},
    )


@router.patch("/job_evaluation")
async def job_evaluation(
    data_task: EvaluationSchema,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    check_user_admin(user_data.role)
    query = await db.scalars(select(TaskModel).filter(
            TaskModel.id == data_task.id,
            TaskModel.name == data_task.name,
            TaskModel.team_id == user_data.team_id,
        ))
    task = query.first()
    check_absence_task(task)
    await add_evaluation_db(job_evaluation=data_task.job_evaluation, task=task, db=db)
    return {
        "message": f"Задача {data_task.name} выполнена на {data_task.job_evaluation} баллов"
    }


# @router.get("/tasks_user", response_model=List[JobResultSchema])
@router.get("/tasks_user/{task_id}")
async def get_tasks_user(
    task_id: int,
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    average_grade = await get_average_grade(task_id=task_id, db=db)
    query = await db.scalars(select(TaskModel).filter(
        TaskModel.executor_id == task_id
    ))
    tasks_user = query.all()
    return templates.TemplateResponse(
        request,
        "tasks/tasks_user.html",
        {
            "request": request,
            "current_user": user_data,
            "tasks_user": tasks_user,
            "average_grade": average_grade,
        },
    )


# @router.get("/task_user/{task_id}", response_model=List[JobResultSchema])
@router.get("/task_user/{task_id}")
async def get_task_user(
    task_id: int,
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    query = await db.execute(select(TaskModel).filter(TaskModel.id == task_id).options(
        selectinload(TaskModel.executor),
        selectinload(TaskModel.team),
        selectinload(TaskModel.chat).joinedload(MessageModel.sender),

        ))
    task_user = query.scalars().first()

    return templates.TemplateResponse(
        request,
        "tasks/task.html",
        {
            "current_user": user_data,
            "task_user": task_user,
            "chat": task_user.chat[::-1],
        },
    )
