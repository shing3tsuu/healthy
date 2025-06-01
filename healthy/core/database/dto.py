from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from .structures import *

@dataclass(slots=True, kw_only=True, frozen=True)
class UserDomain:
    id: int
    tg_id: int
    username: Optional[str]
    first_name: Optional[str]
    timezone: str
    registration_date: datetime


@dataclass(slots=True, kw_only=True, frozen=True)
class HabitDomain:
    id: int
    name: str
    cost_per_unit: Optional[float]
    info: list[Info]
    hints: list[Hint]


@dataclass(slots=True, kw_only=True, frozen=True)
class UserHabitDomain:
    id: int
    user_id: int
    habit_id: int
    start_date: datetime
    last_relapse: Optional[datetime]
    saved_money: int


@dataclass(slots=True, kw_only=True, frozen=True)
class InfoDomain:
    id: int
    name: str
    description: str
    habit_id: int


@dataclass(slots=True, kw_only=True, frozen=True)
class HintDomain:
    id: int
    name: str
    description: str
    habit_id: int


@dataclass(slots=True, kw_only=True, frozen=True)
class ReminderDomain:
    id: int
    reminder_type: str
    scheduled_time: time
    is_active: bool
    user_habit_id: int


@dataclass(slots=True, kw_only=True, frozen=True)
class RelapseHistoryDomain:
    id: int
    relapse_time: datetime
    reason: Optional[str]
    user_habit_id: int