from typing import Awaitable, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date, time

from core.database.dto import *

class BaseUserGateway(ABC):
    @abstractmethod
    async def create_user(
            self,
            tg_id: int,
            username: Optional[str],
            first_name: Optional[str],
            timezone: str
    ) -> UserDomain:
        """
        Create a new user in the database.
        tg_id: Telegram ID of the user.
        username: Telegram profile name of the user.
        first_name: TextInput name of the user.
        timezone: pytz.timezone of the user.
        :return UserDomain model of the user
        """
        raise NotImplementedError()

    @abstractmethod
    async def add_admin_habit(
            self,
            name: str,
            cost_per_unit: Optional[int],
    ) -> HabitDomain:
        """
        Create a new habit in database by admin.
        name: name of the habit.
        cost_per_unit: cost per unit (day) of the habit.
        :return HabitDomain model of the habit
        """
        raise NotImplementedError()

    @abstractmethod
    async def add_admin_hint(
            self,
            name: str,
            description: str,
            habit_id: int
    ) -> HintDomain:
        """
        Create a new hint to habit in database by admin.
        name: name of the hint.
        description: description of the hint.
        habit_id: habit id of the hint.
        :return HintDomain model of the habit
        """
        raise NotImplementedError()
