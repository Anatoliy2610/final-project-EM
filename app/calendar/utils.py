from datetime import date, datetime
from typing import Any, Dict, List


def get_data_meeting(user_events, user_data):
    for meeting in user_data.meetings:
        user_events.append(
            {
                "type": "meeting",
                "id": meeting.id,
                "title": meeting.name,
                "start_time": meeting.datetime_beginning,
                "end_time": meeting.datetime_end,
            }
        )


def get_data_task(user_events, user_data):
    for task in user_data.tasks:
        user_events.append(
            {
                "type": "task",
                "id": task.id,
                "title": task.name,
                "due_date": task.dedline,
            }
        )


def get_monthly_calendar_data(monthly_calendar_data, cal, year, month, user_events):
    if not user_events:
        return
    for week in cal:
        for day_num in week:
            if day_num == 0:
                continue
            current_day_date = date(year, month, day_num)
            day_details: Dict[str, Any] = {
                "date": current_day_date,
                "events_list": [],
            }

            for event in user_events:
                if event["type"] == "meeting":
                    if event["start_time"].date() == current_day_date:
                        day_details["events_list"].append(event)
                elif event["type"] == "task":
                    if (
                        event["due_date"]
                        and event["due_date"].date() == current_day_date
                    ):
                        day_details["events_list"].append(event)
            day_details["events_list"].sort(
                key=lambda x: (
                    0 if x["type"] == "meeting" else 1,  # Сначала встречи
                    x.get("start_time", datetime.max),  # По времени начала встречи
                )
            )

            monthly_calendar_data[current_day_date.isoformat()] = (
                day_details  # Используем ISO формат даты как ключ
            )


def get_daily_calendar_data(monthly_calendar_data, daily_calendar_data):
    for day_key, day_info in monthly_calendar_data.items():
        hours_data: Dict[int, List[Dict[str, Any]]] = {}
        for item in day_info["events_list"]:
            hour = -1  # Для задач без конкретного времени
            if item["type"] == "meeting":
                hour = item["start_time"].hour
            if hour not in hours_data:
                hours_data[hour] = []
            hours_data[hour].append(item)
        for h in hours_data:
            hours_data[h].sort(key=lambda x: x.get("start_time", datetime.max))
        daily_calendar_data[day_key] = hours_data
