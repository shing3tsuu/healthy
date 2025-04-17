from typing import Awaitable, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date, time

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from database import User, Habit, UserHabit, Info, Hint, Reminder, RelapseHistory


@dataclass(slots=True, kw_only=True)
class UserDomain:
    id: int
    tg_id: int
    username: Optional[str]
    first_name: Optional[str]
    timezone: str
    registration_date: datetime


@dataclass(slots=True, kw_only=True)
class HabitDomain:
    id: int
    name: str
    cost_per_unit: Optional[float]
    info: list[InfoDomain]
    hints: list[HintDomain]


@dataclass(slots=True, kw_only=True)
class UserHabitDomain:
    id: int
    user_id: int
    habit_id: int
    start_date: datetime
    last_relapse: Optional[datetime]
    saved_money: int


@dataclass(slots=True, kw_only=True)
class InfoDomain:
    id: int
    name: str
    description: str
    habit_id: int


@dataclass(slots=True, kw_only=True)
class HintDomain:
    id: int
    name: str
    description: str
    habit_id: int


@dataclass(slots=True, kw_only=True)
class ReminderDomain:
    id: int
    reminder_type: str
    scheduled_time: time
    is_active: bool
    user_habit_id: int


@dataclass(slots=True, kw_only=True)
class RelapseHistoryDomain:
    id: int
    relapse_time: datetime
    reason: Optional[str]
    user_habit_id: int


class BaseUserGateWay(ABC):
    @abstractmethod
    async def create_user(self, tg_id: int, username: Optional[str], first_name: Optional[str], timezone: str) -> UserDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_user_by_tg_id(self, tg_id: int) -> UserDomain:
        raise NotImplementedError()


    @abstractmethod
    async def create_user_habit(self, user_id: int, habit_id: int, start_date: datetime) -> UserHabitDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_user_habit_by_id(self, user_habit_id: int) -> UserHabitDomain:
        raise NotImplementedError()

    @abstractmethod
    async def create_reminder(self, user_habit_id: int, reminder_type: str, scheduled_time: time,
                              is_active: bool) -> ReminderDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_reminder_by_id(self, reminder_id: int) -> ReminderDomain:
        raise NotImplementedError()

    @abstractmethod
    async def create_relapse_history(self, user_habit_id: int, relapse_time: datetime,
                                     reason: Optional[str]) -> RelapseHistoryDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_relapse_history_by_id(self, relapse_history_id: int) -> RelapseHistoryDomain:
        raise NotImplementedError()

class BaseHabitGateWay(ABC):
    @abstractmethod
    async def create_habit(self, name: str, cost_per_unit: Optional[float], info: list[Info], hints: list[Hint]) -> HabitDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_all_habits(self) -> list[HabitDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def create_info(self, habit_id: int, name: str, description: str) -> InfoDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_all_infos(self, habit_id: int) -> list[InfoDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def create_hint(self, habit_id: int, name: str, description: str) -> HintDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_all_hints(self, habit_id: int) -> list[HintDomain]:
        raise NotImplementedError()