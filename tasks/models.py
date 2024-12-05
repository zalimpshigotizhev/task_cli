from dataclasses import dataclass
from datetime import datetime, timedelta

from rich.console import Group
from rich.padding import Padding
from rich.text import Text


@dataclass
class Task:
        """dataclass для представление единицы задачи"""
        title: str
        description: str
        category: str
        deadline: str
        priority: str
        status: bool

        id: int | None = None

        def repr_status(self) -> str:
            """
            :return: Возвращает строку исходя от статуса задачи
            """
            return "✅ Выполнено" if self.status else "❌ Не выполнено"

        def timing(self) -> timedelta:
            """
            Вычисляет время, которое осталось до конца срока
            выполнение задачи
            """
            parsing_deadline = datetime.strptime(
                self.deadline, "%Y-%m-%dT%H:%M:%S.%f"
            )
            now = datetime.now()
            return parsing_deadline - now

        def __rich__(self) -> Padding:
            """
            Метод, который предлагает фреймворк `rich`.
            Repr для `rich.console.Console`
            :return: Padding[Group[Text]] - грубо говоря.
            """
            timing = self.timing()
            task = Group(
                Text.assemble((f"{self.title}", "blue")),
                Text.assemble(("ID: ", "bold yellow"), (f"{self.id}", "white")),
                Text.assemble(("Описание: ", "bold yellow"), (f"{self.description}", "white")),
                Text.assemble(("Категория: ", "bold yellow"), (f"{self.category}", "white")),
                Text.assemble(
                    ("Осталось времени: ", "bold yellow"),
                    (f"{timing}", "white" if timing > timedelta(hours=7) else "red")
                ),
                Text.assemble(("Приоритет: ", "bold yellow"), (f"{self.priority}", "white")),
                Text.assemble(("Статус: ", "bold yellow"), (f"{self.repr_status()}", "white")),
                Text.assemble(),
                Text.assemble(("", "bold yellow")),
            )
            return Padding(
                task,
                pad=(1,1)
            )
