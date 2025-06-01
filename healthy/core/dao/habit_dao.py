from typing import Awaitable, Optional
from datetime import datetime, date, time
from abc import ABC, abstractmethod

from core.database.dto import HabitDomain, InfoDomain, HintDomain

class BaseHabitGateway(ABC):
    @abstractmethod
    async def create_habit(self, name: str, cost_per_unit: Optional[float], info: list[InfoDomain], hints: list[HintDomain]) -> HabitDomain:
        raise NotImplementedError()
    # Создание привычки

    @abstractmethod
    async def get_all_habits(self) -> list[HabitDomain]:
        raise NotImplementedError()
    # Получение всех привычек, подзагрузка подсказок и информации