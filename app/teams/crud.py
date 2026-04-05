from sqlalchemy import select

from app.teams.models import TeamModel
from app.teams.utils import check_availability_team, check_role, check_user_absence_role



async def get_team_db(name_team, db):
    query = await db.scalars(select(TeamModel).filter(TeamModel.name == name_team))
    team = query.first()
    return team


async def add_team_db(data_team, user_data, db):
    query = await db.scalars(select(TeamModel).filter(TeamModel.name == data_team.name))
    team = query.first()
    check_availability_team(team=team)
    check_user_absence_role(role=user_data.role)
    db_team = TeamModel(name=data_team.name)
    db.add(db_team)
    user_data.team_id = team.id
    user_data.role = "админ команды"
    await db.commit()
    await db.refresh(db_team)


async def update_data_user_db(data_user, data_team, db):
    query = await db.scalars(select(TeamModel).filter(TeamModel.name == data_team.name))
    new_team_id = query.first()
    data_user.team_id = new_team_id.id
    data_user.role = "админ команды"
    await db.commit()


async def add_user_to_team_db(user, admin_data, new_data_user, db):
    check_role(new_data_user.role)
    user.role = new_data_user.role
    user.team_id = admin_data.team_id
    await db.commit()


async def update_user_to_team_db(user, new_role, db):
    check_role(new_role)
    user.role = new_role
    await db.commit()
