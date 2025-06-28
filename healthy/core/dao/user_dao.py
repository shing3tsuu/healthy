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
        by tg_id: Telegram ID of the user.
        by username: Telegram profile name of the user.
        by first_name: TextInput name of the user.
        by timezone: pytz.timezone of the user.
        :return UserDomain pydantic model of the user
        """
        raise NotImplementedError()
