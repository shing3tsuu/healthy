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
