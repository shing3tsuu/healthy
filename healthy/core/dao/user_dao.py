from typing import Awaitable, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date, time

from core.database.dto import UserDomain, UserHabitDomain, ReminderDomain, RelapseHistoryDomain

class BaseUserGateway(ABC):
    @abstractmethod
    async def create_user(self, tg_id: int, username: Optional[str], first_name: Optional[str], timezone: str) -> UserDomain:
        raise NotImplementedError()
    # Создание пользователя в БД

    @abstractmethod
    async def get_user_by_tg_id(self, tg_id: int) -> UserDomain:
        raise NotImplementedError()
    # Получение пользователя по его Telegram ID

    @abstractmethod
    async def create_user_habit(self, user_id: int, habit_id: int, start_date: datetime) -> UserHabitDomain:
        raise NotImplementedError()
    # Создание привычки пользователя

    @abstractmethod
    async def get_user_habit_by_id(self, user_id: int) -> UserHabitDomain:
        raise NotImplementedError()
    # Получение привычки пользователя по его User ID