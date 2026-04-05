from datetime import datetime

from pydantic import BaseModel


class CalendarSchemas(BaseModel):
    first_data: datetime
    second_data: datetime = None
