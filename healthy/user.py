from shutil import which
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
    async def create_habit(self, name: str, cost_per_unit: Optional[float], info: list[Info], hints: list[Hint]) -> HabitDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_all_habits(self) -> list[HabitDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def create_user_habit(self, user_id: int, habit_id: int, start_date: datetime) -> UserHabitDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_user_habit_by_id(self, user_habit_id: int) -> UserHabitDomain:
        raise NotImplementedError()

    @abstractmethod
    async def create_reminder(self, user_habit_id: int, reminder_type: str, scheduled_time: time, is_active: bool) -> ReminderDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_reminder_by_id(self, reminder_id: int) -> ReminderDomain:
        raise NotImplementedError()

    @abstractmethod
    async def create_relapse_history(self, user_habit_id: int, relapse_time: datetime, reason: Optional[str]) -> RelapseHistoryDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_relapse_history_by_id(self, relapse_history_id: int) -> RelapseHistoryDomain:
        raise NotImplementedError()


class UserGateWay(BaseUserGateWay):
    __slots__ = ("_session", )

    def __init__(self, session):
        self._session = session

    async def create_user(self, tg_id: int, username: Optional[str], first_name: Optional[str], timezone: str) -> UserDomain:
        statement = (
            insert(User).values(
                tg_id=tg_id, username=username, first_name=first_name, timezone=timezone
                )
            .on_conflict_do_update(
                index_elements=['tg_id'],set_={'username': username,'first_name': first_name,'timezone': timezone}
                ).
            returning(User)
        )

        result = await self._session.execute(statement)
        user = result.scalar_one()
        await self._session.flush()

        return UserDomain(
            id=user.id,
            tg_id=user.tg_id,
            username=user.username,
            first_name=user.first_name,
            timezone=user.timezone,
            registration_date=user.registration_date
        )

    async def get_user_by_tg_id(self, user_tg_id: int) -> Optional[UserDomain]:
        statement = select(User).where(User.tg_id == user_tg_id)
        result = await self._session.execute(statement)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundError(f"User with tg_id={user_tg_id} not found")

        return UserDomain(
            id=user.id,
            tg_id=user.tg_id,
            username=user.username,
            first_name=user.first_name,
            timezone=user.timezone,
            registration_date=user.registration_date
        )

    async def create_habit(self, name: str, cost_per_unit: Optional[float], info: list[Info], hints: list[Hint]) -> HabitDomain:
        existing_statement = select(Habit).where(Habit.name == name)
        existing = await self._session.scalar(existing_statement)

        if existing:
            raise ConflictError(f"Habit with name={name} already exists")

        statement = (
            insert(Habit).values(
                name=name, cost_per_unit=cost_per_unit
            )
        )
        result = await self._session.execute(statement)
        habit = result.scalar_one()
        await self._session.flush()

        return HabitDomain(
            id=habit.id,
            name=habit.name,
            cost_per_unit=habit.cost_per_unit,
            info=habit.info,
            hints=habit.hints
        )

    async def get_all_habits(self) -> list[HabitDomain]:
        statement = select(Habit).options(joinedload(Habit.info), joinedload(Habit.hints))
        result = await self._session.execute(statement)
        habits = result.scalars().all()
        await self._session.flush()

        return [
            HabitDomain(
                id=habit.id,
                name=habit.name,
                cost_per_unit=habit.cost_per_unit,
                info=habit.info,
                hints=habit.hints
            ) for habit in habits ]

    async def create_user_habit(self, user_id: int, habit_id: int, start_date: datetime) -> UserHabitDomain:
        existing_statement = select(UserHabit).where(
            (UserHabit.user_id == user_id) &
            (UserHabit.habit_id == habit_id)
        )
        existing = await self._session.scalar(existing_statement)

        if existing:
            raise ConflictError(f"User already have this habit")

        statement = (
            insert(UserHabit).values(
                user_id=user_id, habit_id=habit_id, start_date=start_date, last_relapse=None, saved_money=0
            )
            .returning(UserHabit)
        )
        result = await self._session.execute(statement)
        user_habit = result.scalar_one()
        await self._session.flush()

        return UserHabitDomain(
            id=user_habit.id,
            user_id=user_habit.user_id,
            habit_id=user_habit.habit_id,
            start_date=user_habit.start_date,
            last_relapse=user_habit.last_relapse,
            saved_money=user_habit.saved_money
        )

    async def get_user_habit_by_id(self, user_id: int) -> Optional[list[UserHabitDomain]]:
        statement = (
            select(UserHabit)
            .where(UserHabit.user_id == user_id)
            .options(joinedload(UserHabit.habit))
        )

        result = await self._session.execute(statement)
        user_habits = result.scalars().all()
        await self._session.flush()

        return [
            UserHabitDomain(
            id=user_habit.id,
            user_id=user_habit.user_id,
            habit_id=user_habit.habit_id,
            start_date=user_habit.start_date,
            last_relapse=user_habit.last_relapse,
            saved_money=user_habit.saved_money
        ) for user_habit in user_habits ]