from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.teams.schemas import TeamSchema
from app.users.schemas import User


class MeetingSchema(BaseModel):
    name: str
    datetime_beginning: datetime
    datetime_end: datetime
    team_id: int | None 
    team: TeamSchema
    participants: List[User]


class MeetinAddSchema(BaseModel):
    name: str
    datetime_beginning: datetime
    participants: List[int]


class MeetingSchemaDelete(BaseModel):
    id: int


class MeetingsUserSchema(BaseModel):
    name: str
    datetime_beginning: datetime
    datetime_end: datetime
    team_id: int
    team: TeamSchema
    participants: List[User]
