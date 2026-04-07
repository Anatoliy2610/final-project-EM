from sqladmin import ModelView

from app.meetings.models import MeetingModel
from app.tasks.models import TaskModel
from app.teams.models import TeamModel
from app.users.models import UserModel


class UserAdmin(ModelView, model=UserModel):
    column_list = [
        UserModel.id,
        UserModel.email,
        UserModel.role,
        UserModel.team_id,
        UserModel.team,
        UserModel.hash_password,
        UserModel.meetings,
    ]


class TeamAdmin(ModelView, model=TeamModel):
    column_list = [TeamModel.id, TeamModel.name]


class TaskAdmin(ModelView, model=TaskModel):
    column_list = [
        TaskModel.id,
        TaskModel.name,
        TaskModel.executor_id,
        TaskModel.executor,
        TaskModel.status,
        TaskModel.dedline,
        TaskModel.description,
        TaskModel.job_evaluation,
        TaskModel.team_id,
        TaskModel.team,
    ]


class MeetingAdmin(ModelView, model=MeetingModel):
    column_list = [
        MeetingModel.id,
        MeetingModel.name,
        MeetingModel.datetime_beginning,
        MeetingModel.datetime_end,
        MeetingModel.team_id,
        MeetingModel.team,
        MeetingModel.participants,
    ]
