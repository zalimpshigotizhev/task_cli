import abc
import json
import os
from collections import defaultdict
from dataclasses import asdict

from settings import settings
from tasks.models import Task
from utils.manager_id import ManagerID


class TaskManagerI(abc.ABC):
    """Абстрактный класс для работы с БД"""
    @abc.abstractmethod
    def add_task(self, task: Task):
        """Добавить задачу в БД."""
        ...

    @abc.abstractmethod
    def find_by_id(self, all_tasks: list[dict], task_id: int):
        """Найти задачу по ID."""
        ...

    @abc.abstractmethod
    def remove_task(self, task: Task):
        """Удалить определенную задачу"""
        ...

    @abc.abstractmethod
    def get_tasks(self):
        """Вывести список задач."""
        ...

    @abc.abstractmethod
    def complete_task(self, task: Task):
        """Отметить задачу как выполненную."""
        ...

    @abc.abstractmethod
    def incomplete_task(self, task: Task):
        """Отметить задачу как невыполненную."""
        ...



class TaskManagerJSON(TaskManagerI):
    """Класс для управления списком задач."""
    def __init__(self):
        self.path = settings.path_db
        self.manager_id = ManagerID(settings.path_auto_incr)
        self.id_path = settings.path_auto_incr
        self.categories = dict()

        # Если файл не существует, то создаем
        if not os.path.exists(self.path):
            with open(self.path, 'w', encoding='utf-8') as file:
                json.dump([], file, ensure_ascii=False, indent=4)

    def load_data(self) -> list[dict]:
        """
        Достать список из файла JSON
        :return: Список с задачами в виде словарей.
        """
        with open(self.path, 'r', encoding='utf-8') as file:
            all_tasks = json.load(file)
        return all_tasks

    def save_data(self, all_tasks: list[dict]) -> None:
        """Сохранить новый список в файле JSON"""
        if not all_tasks or type(all_tasks) is not list:
            all_tasks = []
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(all_tasks, file, ensure_ascii=False, indent=4)

    def find_by_id(self, all_tasks: list[dict], task_id: int) -> int | None:
        """
        Находит задачу по ID. Бинарный поиск.
        :param all_tasks: Список с задачами в виде словаря.
        :param task_id: ID Задачи.
        :return: Либо индекс задачи в `all_tasks`, либо
        если ничего не найдено `None`.
        """
        left = 0
        right = len(all_tasks) - 1
        while left <= right:
            middle = (left + right) // 2
            if all_tasks[middle].get("id") == task_id:
                return middle

            elif all_tasks[middle].get("id") < task_id:
                left = middle + 1

            elif all_tasks[middle].get("id") > task_id:
                right = middle - 1
        return None

    def add_task(self, task: Task) -> None:
        """Добавить задачу в список."""
        all_tasks = self.load_data()
        task_dict = asdict(task)
        task_dict["id"] = ManagerID(self.id_path).increment()
        all_tasks.append(task_dict)
        self.save_data(all_tasks)

    def edit_task(self, task: Task, key: str, editable: str) -> None:
        """
        Изменить задачу по ключу в словаре.
        :param task: Задача в которой будем менять
        :param key: Ключ также элемент задачи, который будем менять.
        :param editable: Новое значение для элемента.
        """
        all_tasks = self.load_data()
        task_id = self.find_by_id(all_tasks, task.id)
        task_dict = all_tasks[task_id]
        task_dict[key] = editable
        self.save_data(all_tasks)

    def remove_task(self, task_id: int):
        """Удалить задачу по имени."""
        all_tasks = self.load_data()
        task = self.find_by_id(all_tasks, task_id)
        all_tasks.pop(task)
        self.save_data(all_tasks)

    def get_cats(self) -> dict[str, list[Task]]:
        """
        Получить всевозможные категории из задач.
        :return: Возвращается название категории ключом,
        а значением список с принадлежащими категорию
        задач.
        """
        tasks = self.get_tasks()
        cat_with_task = defaultdict(list)
        for task in tasks:
            cat_with_task[task.category].append(task)
        return cat_with_task

    def get_tasks(self) -> list[Task]:
        """Вывести список задач."""
        all_tasks = []
        for task_map in self.load_data():
            all_tasks.append(Task(**task_map))
        return all_tasks

    def get_incompleted(self) -> list[Task]:
        """Получить список с не выполненными задачами."""
        all_tasks = self.get_tasks()
        complited_tasks = [task for task in all_tasks
                           if not task.status]
        return complited_tasks

    def complete_task(self, task: Task):
        """Отметить задачу как выполненную."""
        all_tasks = self.load_data()
        task_id = self.find_by_id(all_tasks=all_tasks, task_id=task.id)
        curr_task = all_tasks[task_id]
        curr_task["status"] = True
        self.save_data(all_tasks)

    def incomplete_task(self, task: Task):
        """Отметить задачу как невыполненную."""
        all_tasks = self.load_data()
        task_id = self.find_by_id(all_tasks=all_tasks, task_id=task.id)
        curr_task = all_tasks[task_id]
        curr_task["status"] = False
        self.save_data(all_tasks)

    def find_to_entry_title(self, entry_str: str) -> list[Task]:
        """
        Поиск по вхождениям строки в `title` задач
        :param entry_str: Строка которая должна присутствовать
        в задаче.
        :return: Список с задачами в которых присутствует подстрока
        """
        all_tasks = self.load_data()
        entry_str = entry_str.lower()
        finded_tasks = []
        for task in all_tasks:
            title = task.get("title").lower()
            if entry_str in title:
                finded_tasks.append(Task(**task))
        return finded_tasks
