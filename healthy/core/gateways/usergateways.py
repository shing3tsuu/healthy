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
from core.database.structures import *
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

        await self._session.execute(statement)

    @DatabaseLoggerHandler(enable_timing=True)
    async def add_admin_habit(self, name: str, cost_per_unit: int | None) -> HabitDomain:
        statement = (
            insert(Habit).values(
                name=name, cost_per_unit=cost_per_unit
            )
        )

        await self._session.execute(statement)

    @DatabaseLoggerHandler(enable_timing=True)
    async def add_admin_hint(self, name: str, description: str, habit_id: int) -> HintDomain:
        statement = (
            insert(Hint).values(
                name=name, description=description, habit_id=habit_id
            )
        )

        await self._session.execute(statement)
