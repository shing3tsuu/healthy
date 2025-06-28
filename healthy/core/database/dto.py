from pydantic import BaseModel, validator, constr
from typing import Optional, List
from datetime import datetime
import pytz

from .structures import *

class UserDomain(BaseModel):
    id: int
    tg_id: int
    username: constr(min_length=1, max_length=50)
    first_name: constr(min_length=1, max_length=50)
    timezone: str
    registration_date: datetime

    @staticmethod
    @validator("timezone")
    def validate_timezone(value):
        try:
            pytz.timezone(value)
            return value
        except pytz.UnknownTimeZoneError:
            raise ValueError("Invalid timezone")

class HabitDomain(BaseModel):
    id: int
    name: str
    cost_per_unit: Optional[float] = None
    info: List["InfoDomain"]
    hints: List["HintDomain"]

class UserHabitDomain(BaseModel):
    id: int
    user_id: int
    habit_id: int
    start_date: datetime
    last_relapse: Optional[datetime]
    saved_money: Optional[float] = None

class InfoDomain(BaseModel):
    id: int
    name: constr(min_length=1, max_length=50)
    description: str
    habit_id: int

class HintDomain(BaseModel):
    id: int
    name: constr(min_length=1, max_length=50)
    description: str
    habit_id: int

class ReminderDomain(BaseModel):
    id: int
    reminder_type: str
    scheduled_time: time
    is_active: bool
    user_habit_id: int

class RelapseHistoryDomain(BaseModel):
    id: int
    relapse_time: datetime
    reason: Optional[constr(min_length=1, max_length=100)]
    user_habit_id: int
