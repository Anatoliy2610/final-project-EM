import calendar
from datetime import date
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse


from app.calendar.crud import CalendarCRUD
from app.calendar.dependencies import get_calendar_crud
from app.calendar.utils import (
    get_daily_calendar_data,
    get_data_meeting,
    get_data_task,
    get_monthly_calendar_data,
)
from app.core.config import templates
from app.users.dependencies import get_current_user
from app.users.models import UserModel

router = APIRouter(tags=["Календарь"])


@router.get("/user_calendar", response_class=HTMLResponse)
async def get_user_calendar(
    request: Request,
    meeting_crud: CalendarCRUD = Depends(get_calendar_crud),
    current_user: UserModel = Depends(get_current_user),
):
    today = date.today()
    year, month = today.year, today.month
    cal = calendar.monthcalendar(year, month)
    monthly_calendar_data: Dict[int, Dict[str, Any]] = {}
    user_events: List[Dict[str, Any]] = []
    user_data = await meeting_crud.get_user_db(user=current_user)
    get_data_meeting(user_events=user_events, user_data=user_data)
    get_data_task(user_events=user_events, user_data=user_data)
    get_monthly_calendar_data(
        monthly_calendar_data=monthly_calendar_data,
        cal=cal,
        year=year,
        month=month,
        user_events=user_events,
    )

    daily_calendar_data: Dict[str, Dict[int, List[Dict[str, Any]]]] = {}
    get_daily_calendar_data(
        monthly_calendar_data, daily_calendar_data=daily_calendar_data
    )
    return templates.TemplateResponse(
        request,
        "calendar/calendar.html",
        {
            "request": request,
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "calendar_grid": cal,
            "monthly_events": monthly_calendar_data,
            "daily_schedule": daily_calendar_data,
            "current_user": current_user,
            "date": date,
        },
    )
