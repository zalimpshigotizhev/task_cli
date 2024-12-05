from typing import Callable
from datetime import datetime, timedelta
import math
import re

from rich.console import Group, Console
from rich.padding import Padding
from rich.prompt import Prompt
from rich.style import Style
from rich.text import Text

from settings import settings
from tasks.db import TaskManagerJSON
from tasks.models import Task
from utils import const
from utils.funcs import make_panel, choices_options


class TaskCLI:
    def __init__(self):
        self.console = Console()
        self.manager = TaskManagerJSON()
        self.limited = settings.limited
        self.options = {
            # "0": self.back,
            "102": ("Разбить на категории", self.present_cats),
            "103": ("Показать только не выполненные", self.present_not_comple)
        }

    def get_tasks(self) -> None:
        """
        Показать все задачи, с разбиением на страницы
        до кол-ства, который указан в `settings.settings`.
        Также запрашивает код, по которому можно выбрать либо
        определенную задачу, либо воспользоваться опцией.
        :return:
        """
        while True:
            self.console.clear()
            # Информационная панель
            tasks = self.manager.get_tasks()
            choice = self.repr_tasks(tasks=tasks, title="Список всех задач")
            t_option = self.options.get(choice)
            if choice == "":
                return
            elif t_option is not None:
                title, option = t_option
                option()

    def paginate(self, tasks: list) -> iter:
        """
        Генератор для постраничного разбиения задач.

        :return: Генератор списков с задачами.
        """
        if not tasks or self.limited <= 0:
            yield []  # Возвращаем пустую страницу, если задач нет или ограничение некорректно
            return

        count_pages = math.ceil(len(tasks) / self.limited)
        for page in range(count_pages):
            start = page * self.limited
            end = start + self.limited
            yield tasks[start:end]


    def abb_repr_task(self, num: int, task: Task) -> Group:
        """
        Генерирует сокращенное отображение для задачи.
        :param num:
        :param task:
        :return:
        """
        # sos - это маркер, который
        # оповещает о том, что время либо истекло,
        # либо осталось 7 часов до истечения.

        sos = Text(
            "SOS",
            style=Style(
                bgcolor="red"
            )
        )

        title = Text.assemble(
            (f"{num}) ", "dark_blue"),
            (f"{task.title} ", "blue3"),
            style=Style(

            )
        )
        if task.timing() < timedelta(hours=7):
            title.append(
                sos
            )


        row1 = Text.assemble(
            ("ID:", "bold bright_black"),
            (f"{task.id}", "white"), "\t",
            ("Статус: ", "bold bright_black"),
            (f"{task.repr_status()}", "white")
        )
        row2 = Text.assemble(
            "\t",
            ("Приоритет: ", "bold bright_black"),
            (f"{task.priority}", "white")
        )

        task = Group(
            title,
            row1,
            row2
        )
        return task

    def delete_task(self, task: Task) -> None:
        """ Отображение для удаления определенных задач."""
        repr_result = [
            f"Задача \"{task.title}\" удалена!",
            task
        ]
        self.manager.remove_task(task.id)
        self.status_process("🧹🪣  Задача удалена!", task)

    def complete_task(self, task: Task) -> None:
        """ Отображение для изменения статуса
        задачи на выполненно"""
        self.manager.complete_task(task)
        self.status_process("✔  Задача выполнена!", task)

    def incomplete_task(self, task: Task) -> None:
        """ Отображение для изменения статуса
        задачи на не выполненно"""
        self.manager.incomplete_task(task)
        self.status_process("🔄 Задачу нужно снова выполнить", task)

    def repr_tasks(
            self,
            tasks: list[Task],
            title: str
    ) -> str | None:
        """
        Нормализирует показ списков.

        :param tasks: Список задач.
        :param title: Особенности списка задач
        :return: Либо `choice`, либо `None`.
        """
        if not tasks:
            repr_result = make_panel(
                Text(
                    "Задач пока нет!",
                    Style(color="red")
                ),
                subtitle=False
            )
            self.console.print(repr_result)
            choice = self.console.input(const.ENTER_TO_MENU)
            return choice

        for page_num, page_tasks in enumerate(self.paginate(tasks), 1):
            self.console.clear()
            repr_result = [] # noqa
            task_map = dict()

            repr_result.append(
                "Выберите что нибудь из задач или опций, чтобы взаимодействовать.",
            )

            for num, task in enumerate(page_tasks, 1):
                group = self.abb_repr_task(num, task)
                repr_result.append(
                    Padding(
                        group,
                        pad=(1, 1),
                    )
                )
                task_map[str(num)] = task

            repr_result.append(
                Text(f"Страница: {page_num}"),
            )

            group_choices = choices_options(self.options)
            repr_result.append(
                make_panel(
                    Text.assemble(
                        ("\"\".  ", "bold bright_black"),
                        ("Оставьте пустым, чтобы выйти", "white")
                    ),
                    Text.assemble(
                        (f"1-{self.limited}. ", "bold bright_black"),
                        ("Напишите номер задачи", "white")
                    ),
                    Text.assemble(
                        ("11.  ", "bold bright_black"),
                        "След. страница"
                    ),
                    *group_choices,
                    subtitle=False
                )
            )

            self.console.print(
                make_panel(
                    *repr_result,
                    title=title
                )
            )
            choice = str(self.console.input())
            if choice in task_map.keys():
                select_task = task_map.get(choice)
                self.repr_task_detail(task=select_task)
            elif choice in ["11"]:
                continue
            return choice

    def search_task(self) -> None:
        """
        Отображения для поиска задач по вхождению подстрок
        в название.
        """
        self.console.print(
            make_panel(
                "Напишите строку которая может входить в название задачи.",
                title="Поиск..."
            )
        )
        find_title = self.console.input()
        finded_tasks = self.manager.find_to_entry_title(find_title)
        self.repr_tasks(finded_tasks, "Результаты поиска")

    def present_cats(self) -> None:
        """
        Отображения для категории.
        Функция дает каждой категории код и список
        всех задач для дальнейшего отображения.
        """
        while True:
            self.console.clear()
            repr_result = []
            tasks_map = self.manager.get_cats()
            cats_map = {}
            for num, cat in enumerate(tasks_map.keys(), 1):
                cats_map[str(num)] = cat
                repr_result.append(
                    Text.assemble(
                        (f"{num}) ", "bold bright_black"),
                        f"{cat}"
                    )
                )
            self.console.print(
                make_panel(
                Text(
                    "Выберите категорию:",
                    style=Style(color="bright_black")
                ),
                    *repr_result,
                    title="Категории"
                )
            )
            choice = str(self.console.input())
            cat = cats_map.get(choice)
            tasks = tasks_map.get(cat)
            if choice == "":
                return

            if tasks is not None:
                self.repr_tasks(tasks, title=f"Категория \"{cat}\"")

    def present_not_comple(self) -> None:
        """Показывает только не выполненные задачи"""
        completed_tasks = self.manager.get_incompleted()
        self.repr_tasks(tasks=completed_tasks, title="Задачи ждущие выполнения")

    def add_task(self) -> None:
        """
        Добавить задачу.
        :return:
        """
        self.console.clear()

        self.console.print(
            make_panel(
                "Процесс создание задачи...",
                Text(
                    "Чтобы выйти, оставьте пустым",
                    style=Style(color="bright_black")
                ),
                title="Добавить задачу"
            )
        )
        try:
            title = self.input_and_valid(
                prompt=const.TITLE_HELP_TEXT,
            )

            description = self.input_and_valid(
                prompt=const.DESCRIPTION_HELP_TEXT,
            )

            category = self.input_and_valid(
                prompt=const.CATEGORY_HELP_TEXT,
            )

            deadline = self.term_input_normalize(const.TERM_HELP_TEXT)

            priority = Prompt.ask(
                Text.assemble(
                    (const.PRIORITY_HELP_TEXT, "bold bright_black")
                ),
                choices=["Высокий", "Средний", "Низкий"],
                default="Высокий"
            )

            task = Task(
                id=1,
                title=title,
                description=description,
                category=category,
                deadline=deadline,
                priority=priority,
                status=False,
            )
        except ValueError:
            return

        self.manager.add_task(task=task)
        self.status_process("💾 Новая задача создана!", task)

    def status_process(self, title: str, task: Task) -> None:
        """
        Сообщает о результате обработки данных.
        :param title: Сообщение, которое нужно вывести на экран.
        :param task: Обрабатываемая задача.
        """
        self.console.clear()
        self.console.print(
            make_panel(
                Text.assemble((title, "bold chartreuse1")),
                task
            )
        )
        self.console.input(
            Text.assemble((const.ENTER_TO_MENU, "bold grey42"))
        )

    def term_input_normalize(self, prompt: str) -> str:
        """
        Специальный валидатор для срока задачи.
        :return: isoformat
        """
        while True:
            user_input = self.console.input(
                Text.assemble(
                    (prompt, "bold bright_black")
                )
            )

            match_hours = re.compile(r"h(\d+)").search(user_input)
            match_days = re.compile(r"d(\d+)").search(user_input)
            match_months = re.compile(r"m(\d+)").search(user_input)

            hours = int(match_hours.group(1)) if match_hours else 0
            days = int(match_days.group(1)) if match_days else 0
            months = int(match_months.group(1)) if match_months else 0
            days += months * 30

            if not user_input:
                self.console.print("[red]Сроки не могут пустыми![/red]")
            elif not match_hours and not match_days and not match_months:
                self.console.print("[red]Неправильный формат![/red]")
            else:
                term = timedelta(hours=hours, days=days)
                deadline = datetime.now() + term
                return deadline.isoformat()

    def input_and_valid(
            self,
            prompt: str,
            valid_fn: Callable[[str], bool] | None = None,
            error_message: str | None = None
    ) -> str:
        """
        Функция для спроса и валидации данных.
        :param prompt: Промпт для подсказки, что происходит.
        :param valid_fn: Лямбда, которая проверяет простые условия.
        :param error_message: При неудачном прохождении условий
        выводится ошибка.

        :return:
        """
        while True:
            user_input = self.console.input(
                Text.assemble(
                    (f"{prompt}", "bold bright_black")
                )
            )
            if user_input == "":
                raise ValueError()
            if valid_fn is not None:
                if valid_fn(user_input):
                    return user_input
                else:
                    self.console.print(f"[red]{error_message}[/red]")
            return user_input


    def display_task(
            self,
            task: Task,
            prompt: str,
            options: dict[str, tuple[str, Callable]]
    ) -> None:
        """
        Используется при создании и редактировании задачи.
        :param task: Задача.
        :param prompt: Подсказка.
        :param options: Опции для задачи.
        :return:
        """
        self.console.clear()
        repr_result = [
            Text.assemble(prompt),
            task,
        ]
        info = make_panel(
            Text.assemble(
                ("\"\".  ", "bold bright_black"),
                ("Оставьте пустым, чтобы выйти", "white")
            ),
            *choices_options(options),
            subtitle=False
        )
        self.console.print(
            make_panel(
                *repr_result,
                info,
                title=task.title
            )
        )
        choice = self.console.input()
        if choice in options.keys():
            _, action = options[choice]
            action(task)

    def repr_task_detail(self, task: Task):
        """
        Эндпоинт для показа определенной задачи подробно.
        """
        options = {
            "1": (
                "Отметить выполненным",
                self.complete_task
            ) if not task.status
            else (
                "Отметить не выполненным",
                self.incomplete_task
            ),
            "2": (
                "Редактировать задачу",
                self.edit_task,
            ),
            "3": (
                "Удалить задачу",
                self.delete_task,
            ),
        }
        self.display_task(task=task, prompt="Подробнее о задаче", options=options)

    def edit_task(self, task: Task) -> None:
        """
        Эндпоинт изменение задачи.
        """
        options = {
            "1": ("Изменить название", self.change_title),
            "2": ("Изменить описание", self.change_description),
            "3": ("Изменить категорию", self.change_cat),
            "4": ("Изменить сроки выполнение", self.change_deadline),
            "5": ("Изменить приоритет", self.change_priority),
        }
        self.display_task(task=task, prompt="Изменить задачу", options=options)

    def change_title(self, task: Task) -> None:
        """Процесс изменения названии"""
        new_title = self.input_and_valid("Напишите новое название задачи:")
        self.manager.edit_task(task, key="title", editable=new_title)
        task.title = new_title
        self.status_process("Вы изменили название задачи!", task)

    def change_description(self, task: Task):
        """Процесс изменения описании"""
        new_description = self.input_and_valid("Напишите новое описание задачи:")
        self.manager.edit_task(task, key="description", editable=new_description)
        task.description = new_description
        self.status_process("Вы изменили описание задачи!", task)

    def change_deadline(self, task: Task):
        """Процесс изменения срока"""
        new_deadline = self.term_input_normalize(
            "Введите новый срок выполнения!" + "\n" +
            const.TERM_HELP_TEXT
        )
        self.manager.edit_task(task, key="deadline", editable=new_deadline)
        task.deadline = new_deadline
        self.status_process("Вы изменили сроки задачи!", task)

    def change_cat(self, task: Task):
        """Процесс изменения категории"""
        new_category = self.input_and_valid("Напишите новую категорию задачи:")
        self.manager.edit_task(task, key="category", editable=new_category)
        task.category = new_category
        self.status_process("Вы изменили категорию задачи!", task)

    def change_priority(self, task: Task):
        """Процесс изменения приоритета"""
        new_priority = Prompt.ask(
                Text.assemble(
                    (const.PRIORITY_HELP_TEXT, "bold bright_black")
                ),
                choices=["Высокий", "Средний", "Низкий"],
                default="Высокий"
            )
        self.manager.edit_task(task, key="priority", editable=new_priority)
        task.priority = new_priority
        self.status_process("Вы изменили проритет задачи!", task)
