from fastapi import HTTPException, status



def check_availability_team(team):
    if team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Команда с таким названием уже существует",
        )


def check_user_absence_role(role):
    if role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Вы уже состоите в команде"
        )


def check_user_admin(user_role):
    if user_role != "админ команды":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="У Вас не достаточно прав"
        )


def check_absence_user(user):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователя не существует"
        )


def check_role(role):
    if role not in ("менеджер", "сотрудник"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="такой роли не существует"
        )


def check_user_to_team(user_admin, user_data):
    if user_admin.team_id != user_data.team_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь не состоит в вашей команде",
        )
