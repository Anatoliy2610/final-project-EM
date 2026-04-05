from pydantic import BaseModel


class TeamSchema(BaseModel):
    name: str


class UserTeamSchema(BaseModel):
    email_user: str
    role: str = None


class DeleteUserSChema(BaseModel):
    email_user: str
