
from datetime import date, datetime, time, timedelta
from typing import Optional, List

from sqlalchemy import ForeignKey, String, func, Index, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index('ix_user_tg_id', 'tg_id'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[Optional[str]]
    first_name: Mapped[Optional[str]]
    timezone: Mapped[int]
    registration_date: Mapped[datetime] = mapped_column(server_default=func.now())

    habits: Mapped[List['UserHabit']] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


class Habit(Base):
    __tablename__ = "habits"
    __table_args__ = (
        Index('ix_habit_name', 'name'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    cost_per_unit: Mapped[Optional[float]]

    info: Mapped[List['Info']] = relationship(
        back_populates="habit",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    hints: Mapped[List['Hint']] = relationship(
        back_populates="habit",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


class UserHabit(Base):
    __tablename__ = "user_habits"
    __table_args__ = (
        Index('ix_user_habit', 'user_id', 'habit_id', unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))
    start_date: Mapped[datetime] = mapped_column(server_default=func.now())
    last_relapse: Mapped[Optional[datetime]]
    saved_money: Mapped[int] = mapped_column(default=0)

    user: Mapped['User'] = relationship(back_populates="habits")
    habit: Mapped['Habit'] = relationship(lazy="joined")

    reminders: Mapped[List['Reminder']] = relationship(
        back_populates="user_habit",
        cascade='all, delete-orphan',
        lazy="selectin"
    )

    relapses: Mapped[List['RelapseHistory']] = relationship(
        back_populates="user_habit",
        cascade='all, delete-orphan',
        lazy="dynamic"
    )

    @hybrid_property
    def current_streak(self) -> int:
        reference_date = self.last_relapse or self.start_date
        if isinstance(reference_date, datetime):
            return (datetime.utcnow() - reference_date).days
        return 0


class Info(Base):
    __tablename__ = "info"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(1000))

    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))
    habit: Mapped['Habit'] = relationship(back_populates="info")


class Hint(Base):
    __tablename__ = "hints"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(1000))

    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))
    habit: Mapped['Habit'] = relationship(back_populates="hints")


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (
        Index('ix_reminder_time', 'scheduled_time'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reminder_type: Mapped[str] = mapped_column(String(30))
    scheduled_time: Mapped[time]
    is_active: Mapped[bool] = mapped_column(default=True)

    user_habit_id: Mapped[int] = mapped_column(ForeignKey("user_habits.id"))
    user_habit: Mapped['UserHabit'] = relationship(back_populates="reminders")


class RelapseHistory(Base):
    __tablename__ = "relapse_history"
    __table_args__ = (
        Index('ix_relapse_date', 'relapse_time'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    relapse_time: Mapped[datetime] = mapped_column(server_default=func.now())
    reason: Mapped[Optional[str]] = mapped_column(String(500))

    user_habit_id: Mapped[int] = mapped_column(ForeignKey("user_habits.id"))
    user_habit: Mapped['UserHabit'] = relationship(back_populates="relapses")