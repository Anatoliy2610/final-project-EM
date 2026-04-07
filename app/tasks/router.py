from fastapi import APIRouter, Depends, Request

from app.core.config import templates
from app.core.exceptions import ExceptionService
from app.core.validator import get_validator
from app.tasks.crud import TaskCRUD
from app.tasks.dependencies import get_task_crud
from app.tasks.schemas import (
    EvaluationSchema,
    MessageAddSchema,
    TaskAddSchema,
    TaskDeleteSchema,
    TaskGetResponseSchema,
    TaskUpdateSchema,
)
from app.users.dependencies import get_current_user
from app.users.models import UserModel

router = APIRouter(tags=["Задачи"])


@router.get("/tasks")
async def get_tasks(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    task_crud: TaskCRUD = Depends(get_task_crud),
):
    data_tasks = await task_crud.get_tasks_db(user=user_data)
    return templates.TemplateResponse(
        request=request,
        name="tasks/tasks.html",
        context={"data_tasks": data_tasks, "current_user": user_data},
    )


@router.get("/add_task")
async def get_add_task(
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    task_crud: TaskCRUD = Depends(get_task_crud),
):
    team_users = await task_crud.get_data_for_add_task(user=user_data)
    return templates.TemplateResponse(
        request=request,
        name="tasks/add_task.html",
        context={
            "request": request,
            "current_user": user_data,
            "team_users": team_users,
        },
    )


@router.post("/add_task")
async def add_task(
    data_task: TaskAddSchema,
    user_data: UserModel = Depends(get_current_user),
    validator: ExceptionService = Depends(get_validator),
    task_crud: TaskCRUD = Depends(get_task_crud),
):
    await validator.check_user_admin(user_role=user_data.role)
    await validator.check_executor(data_task=data_task, user=user_data)
    await validator.check_availability_task(data_task=data_task)
    await task_crud.add_task_db(user=user_data, data_task=data_task)
    return {"message": "Задача зарегистрирована"}


@router.get("/update_task/{task_id}", response_model=TaskGetResponseSchema)
async def get_update_task(
    task_id: int,
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    validator: ExceptionService = Depends(get_validator),
    task_crud: TaskCRUD = Depends(get_task_crud),
):
    await validator.check_user_admin(user_role=user_data.role)
    result = await task_crud.get_data_for_update(task_id=task_id, user_data=user_data)
    return templates.TemplateResponse(
        request,
        "tasks/update_task.html",
        {
            "request": request,
            "current_user": user_data,
            "task": result.get("task"),
            "team_users": result.get("team_users"),
        },
    )


@router.patch("/update_task")
async def update_task(
    data_task: TaskUpdateSchema,
    user_data: UserModel = Depends(get_current_user),
    validator: ExceptionService = Depends(get_validator),
    task_crud: TaskCRUD = Depends(get_task_crud),
):
    await validator.check_user_admin(user_role=user_data.role)
    await validator.check_absence_task(user=user_data, data_task=data_task)
    await task_crud.update_task_db(user=user_data, data_task=data_task)
    return {"message": f"Задача {data_task.id} изменена"}


@router.delete("/delete_task")
async def delete_task(
    data_task: TaskDeleteSchema,
    user_data: UserModel = Depends(get_current_user),
    validator: ExceptionService = Depends(get_validator),
    task_crud: TaskCRUD = Depends(get_task_crud),
):
    await validator.check_user_admin(user_role=user_data.role)
    await validator.check_absence_task(user=user_data, data_task=data_task)
    await task_crud.delete_task_db(user=user_data, data_task=data_task)
    return {"message": "Задача удалена"}


@router.get("/job_evaluation/{task_id}", response_model=TaskGetResponseSchema)
async def get_job_evaluation(
    task_id: int,
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    validator: ExceptionService = Depends(get_validator),
    task_crud: TaskCRUD = Depends(get_task_crud),
):
    await validator.check_user_admin(user_role=user_data.role)
    task = await task_crud.get_data_task_db(task_id=task_id, user_data=user_data)
    return templates.TemplateResponse(
        request,
        "tasks/job_evaluation.html",
        {"request": request, "current_user": user_data, "task": task},
    )


@router.patch("/job_evaluation")
async def job_evaluation(
    data_task: EvaluationSchema,
    user_data: UserModel = Depends(get_current_user),
    validator: ExceptionService = Depends(get_validator),
    task_crud: TaskCRUD = Depends(get_task_crud),
):
    await validator.check_user_admin(user_role=user_data.role)
    await validator.check_absence_task(user=user_data, data_task=data_task)
    await validator.check_job_evaluation(job_evaluation=data_task.job_evaluation)
    await task_crud.patch_job_evaluation(user=user_data, data_task=data_task)
    return {
        "message": f"Задача {data_task.name} выполнена на {data_task.job_evaluation} баллов"
    }


@router.post("/add_message")
async def add_message_chat(
    data_chat: MessageAddSchema,
    user_data: UserModel = Depends(get_current_user),
    task_crud: TaskCRUD = Depends(get_task_crud),
):
    await task_crud.add_message_db(user=user_data, data_chat=data_chat)
    return {"message": "Добавлено сообщение в чат к задаче"}


@router.get("/tasks_user/{executor_id}")
async def get_tasks_user(
    executor_id: int,
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    task_crud: TaskCRUD = Depends(get_task_crud),
):
    tasks_user = await task_crud.get_tasks_user_db(executor_id)
    return templates.TemplateResponse(
        request,
        "tasks/tasks_user.html",
        {
            "request": request,
            "current_user": user_data,
            "tasks_user": tasks_user.get("tasks_user"),
            "average_grade": round(tasks_user.get("average_grade"), 1),
        },
    )


@router.get("/task_user/{task_id}")
async def get_task_user(
    task_id: int,
    request: Request,
    user_data: UserModel = Depends(get_current_user),
    task_crud: TaskCRUD = Depends(get_task_crud),
):
    task_user = await task_crud.get_task_user_db(task_id=task_id)
    return templates.TemplateResponse(
        request,
        "tasks/task.html",
        {
            "current_user": user_data,
            "task_user": task_user,
            "chat": task_user.chat[::-1],
        },
    )
