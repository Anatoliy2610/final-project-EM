from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import logger
from app.tasks.models import MessageModel, TaskModel
from app.users.models import UserModel


class TaskCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tasks_db(self, user):
        try:
            query = await self.db.execute(
                select(TaskModel)
                .filter(TaskModel.team_id == user.team_id)
                .options(
                    selectinload(TaskModel.executor),
                    selectinload(TaskModel.team),
                    selectinload(TaskModel.chat),
                )
                .order_by(TaskModel.id)
            )
            return query.scalars().all()
        except DatabaseError as e:
            logger.error(f"Ошибка БД при получении задач: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка при получении данных о задачах"
            )

    async def get_data_for_add_task(self, user):
        try:
            query = await self.db.execute(
                select(UserModel).filter(UserModel.team_id == user.team_id)
            )
            return query.scalars().all()
        except DatabaseError as e:
            logger.error(f"Ошибка БД при получении данных для добавления задачи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Ошибка при получении данных для добавления задачи",
            )

    async def add_task_db(self, user, data_task):
        try:
            try:
                date_parts = data_task.dedline.split("-")
                deadline_date = datetime(
                    int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                )
            except (ValueError, IndexError):
                logger.warning(
                    f"Некорректный формат даты дедлайна: {data_task.dedline}"
                )
                raise HTTPException(
                    status_code=400, detail="Некорректный формат даты дедлайна"
                )
            db_task = TaskModel(
                name=data_task.name,
                executor_id=data_task.executor_id,
                status=data_task.status if data_task.status else "открыто",
                dedline=deadline_date,
                description=data_task.description,
                team_id=user.team_id,
            )
            self.db.add(db_task)
            await self.db.commit()
            await self.db.refresh(db_task)

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании задачи: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось создать задачу из‑за конфликта данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при создании задачи: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при создании задачи"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при создании задачи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при создании задачи",
            )

    async def get_data_for_update(self, task_id, user_data):
        try:
            query_task = await self.db.execute(
                select(TaskModel).filter(
                    TaskModel.id == task_id, TaskModel.team_id == user_data.team_id
                )
            )
            task = query_task.scalars().first()
            query_team = await self.db.execute(
                select(UserModel).filter(UserModel.team_id == user_data.team_id)
            )
            team_users = query_team.scalars().all()
            return {"task": task, "team_users": team_users}
        except DatabaseError as e:
            logger.error(f"Ошибка БД при получении данных для обновления: {e}")
            raise HTTPException(
                status_code=500,
                detail="Ошибка при получении данных для обновления задачи",
            )

    async def update_task_db(self, user, data_task):
        try:
            query = await self.db.execute(
                select(TaskModel).filter(
                    TaskModel.id == data_task.id, TaskModel.team_id == user.team_id
                )
            )
            task = query.scalars().first()
            if data_task.new_name:
                task.name = data_task.new_name
            if data_task.executor_id:
                task.executor_id = data_task.executor_id
            if data_task.status:
                task.status = data_task.status
            if data_task.dedline:
                try:
                    date_parts = data_task.dedline.split("-")
                    task.dedline = datetime(
                        int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                    )
                except (ValueError, IndexError):
                    raise HTTPException(
                        status_code=400, detail="Некорректный формат даты дедлайна"
                    )
            if data_task.description:
                task.description = data_task.description
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при обновлении задачи: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось обновить задачу из‑за конфликта данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при обновлении задачи: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при обновлении задачи"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при обновлении задачи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при обновлении задачи",
            )

    async def delete_task_db(self, user, data_task):
        try:
            query = await self.db.execute(
                select(TaskModel).filter(
                    TaskModel.id == data_task.id,
                    TaskModel.executor_id == data_task.executor_id,
                    TaskModel.team_id == user.team_id,
                )
            )
            task = query.scalars().first()
            await self.db.delete(task)
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при удалении встречи: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось удалить встречу из‑за связанных данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при удалении встречи: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при удалении встречи"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при удалении встречи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при удалении встречи",
            )

    async def get_data_task_db(self, task_id, user_data):
        try:
            query = await self.db.execute(
                select(TaskModel)
                .filter(TaskModel.id == task_id, TaskModel.team_id == user_data.team_id)
                .options(selectinload(TaskModel.executor))
            )
            return query.scalars().first()
        except DatabaseError as e:
            logger.error(f"Ошибка БД при получении пользователей команды: {e}")
            raise HTTPException(
                status_code=500,
                detail="Ошибка при получении данных о пользователях команды",
            )

    async def patch_job_evaluation(self, user, data_task):
        try:
            query = await self.db.execute(
                select(TaskModel).filter(
                    TaskModel.id == data_task.id,
                    TaskModel.name == data_task.name,
                    TaskModel.team_id == user.team_id,
                )
            )
            task = query.scalars().first()
            task.job_evaluation = data_task.job_evaluation
            task.status = "выполнена"
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при удалении встречи: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось удалить встречу из‑за связанных данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при удалении встречи: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при удалении встречи"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при удалении встречи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при удалении встречи",
            )

    async def add_message_db(self, user, data_chat):
        try:
            query_task = await self.db.execute(
                select(TaskModel).filter(
                    TaskModel.id == data_chat.task_id, TaskModel.team_id == user.team_id
                )
            )
            task = query_task.scalars().first()
            db_message = MessageModel(
                message=data_chat.message,
                sender_id=user.id,
                task_id=data_chat.task_id,
            )
            db_message.task = [task]
            self.db.add(db_message)
            await self.db.commit()
            await self.db.refresh(db_message)
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Ошибка целостности данных при удалении встречи: {e}")
            raise HTTPException(
                status_code=409,
                detail="Не удалось удалить встречу из‑за связанных данных",
            )
        except DatabaseError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД при удалении встречи: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка базы данных при удалении встречи"
            )
        except Exception as e:
            await self.db.rollback()
            logger.critical(f"Критическая ошибка при удалении встречи: {e}")
            raise HTTPException(
                status_code=500,
                detail="Произошла непредвиденная ошибка при удалении встречи",
            )

    async def get_tasks_user_db(self, executor_id):
        try:
            avg_result = await self.db.execute(
                select(func.avg(TaskModel.job_evaluation)).filter(
                    TaskModel.executor_id == executor_id,
                    TaskModel.status == "выполнена",
                )
            )
            average_grade = avg_result.scalar() or 0.0
            tasks_result = await self.db.execute(
                select(TaskModel).filter(TaskModel.executor_id == executor_id)
            )
            tasks_user = tasks_result.scalars().all()
            return {"average_grade": average_grade, "tasks_user": tasks_user}
        except DatabaseError as e:
            logger.error(f"Ошибка БД при получении пользователей команды: {e}")
            raise HTTPException(
                status_code=500,
                detail="Ошибка при получении данных о пользователях команды",
            )

    async def get_task_user_db(self, task_id):
        try:
            query = await self.db.execute(
                select(TaskModel)
                .filter(TaskModel.id == task_id)
                .options(
                    selectinload(TaskModel.executor),
                    selectinload(TaskModel.team),
                    selectinload(TaskModel.chat).joinedload(MessageModel.sender),
                )
            )
            return query.scalars().first()
        except DatabaseError as e:
            logger.error(f"Ошибка БД при получении пользователей команды: {e}")
            raise HTTPException(
                status_code=500,
                detail="Ошибка при получении данных о пользователях команды",
            )
