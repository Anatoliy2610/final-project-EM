from pydantic import BaseModel, Field

from app.teams.schemas import TeamSchema


class User(BaseModel):
    email: str
    role: str | None
    team_id: int | None
    team: TeamSchema | None
    hash_password: str


class UserInDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    email: str
    password: str


class UserRegister(BaseModel):
    email: str
    password: str = Field(...)


class UserAuth(BaseModel):
    email: str = Field(...)
    password: str = Field(...)


class UpdateUser(BaseModel):
    email: str = None
    password: str = None
