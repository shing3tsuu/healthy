from typing import Awaitable, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date, time

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC
from functools import wraps
from typing import Callable, Optional
import time as t

from core.dao.user_dao import BaseUserGateway
from .logger_handler import DatabaseLoggerHandler
from core.dao.user_dao import *


class UserGateway(BaseUserGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    @DatabaseLoggerHandler(enable_timing=True)
    async def create_user(self, tg_id: int, username: Optional[str], first_name: Optional[str], timezone: str) -> UserDomain:
        statement = (
            insert(User).values(
                tg_id=tg_id, username=username, first_name=first_name, timezone=timezone, registration_date=datetime.now()
                )
            .on_conflict_do_update(
                index_elements=['tg_id'],set_={'username': username,'first_name': first_name,'timezone': timezone}
                ).
            returning(User)
        )

        result = await self._session.execute(statement)
        user = result.scalar_one()

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
