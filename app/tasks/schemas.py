from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.teams.schemas import TeamSchema
from app.users.schemas import User


class TaskSchema(BaseModel):
    name: str
    extcutor_id: int
    executor_id: User = None
    status: str = None
    dedline: datetime
    description: str = None
    chat: List[str]
    team_id: int
    team: TeamSchema = None


class TaskAddSchema(BaseModel):
    name: str = None
    executor_id: int
    status: str = None
    dedline: str = None
    description: str = None


class TaskUpdateSchema(BaseModel):
    id: int = None
    new_name: str = None
    executor_id: int
    status: str = None
    dedline: str = None
    description: str = None


class TaskGetResponseSchema(BaseModel):
    id: int

    class Congig:
        from_attributes = True


class TaskDeleteSchema(BaseModel):
    id: int
    executor_id: int


class EvaluationSchema(BaseModel):
    id: int
    name: str
    job_evaluation: int


class JobResultSchema(BaseModel):
    name: str
    executor: User
    status: str
    dedline: datetime
    description: str
    chat: str
    job_evaluation: int


class MessageAddSchema(BaseModel):
    task_id: int
    message: str


class ChatSchema(BaseModel):
    task_id: int
