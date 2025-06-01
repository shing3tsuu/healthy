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

from core.dao.habit_dao import *

class HabitGateway(BaseHabitGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_habit(self, name: str, cost_per_unit: Optional[float], info: list[InfoDomain],hints: list[HintDomain]) -> HabitDomain:
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
            ) for habit in habits]