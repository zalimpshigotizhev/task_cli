from dataclasses import asdict
from datetime import datetime

import pytest
import tempfile

from tasks.models import Task
from tasks.views import TaskManagerJSON


@pytest.fixture(name="manager_json", scope="session")
def temp_task_manager():
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_db_file:
        temp_db_file.write("[]")
        temp_db_file.flush()
        manager = TaskManagerJSON()
        manager.path = temp_db_file.name
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_id_file:
        temp_id_file.write("0")
        temp_id_file.flush()
        manager.id_path = temp_id_file.name

    yield manager


@pytest.fixture(name="tasks", scope="session")
def create_tests():
    task1 = Task(
        id=1,
        title="Проверить работает ли создание задачи",
        description="Этот тест отвечает за это",
        category="тесты",
        deadline=datetime.now().isoformat(),
        priority="Высокий",
        status=False
    )
    task2 = Task(
        id=2,
        title="Проверить работает ли создание задачи",
        description="Этот тест отвечает за это",
        category="тесты",
        deadline=datetime.now().isoformat(),
        priority="Высокий",
        status=False
    )
    return [task1, task2]



def test_load_data_empty_file(manager_json):
    tasks = manager_json.load_data()
    assert tasks == [], ("На этом этапе должен загружаться "
                         "пустой список из файла")


def test_add_task(manager_json: TaskManagerJSON, tasks):
    task1, task2 = tasks

    task1_in_dict = asdict(task1)
    task2_in_dict = asdict(task2)

    manager_json.add_task(task1)
    manager_json.add_task(task2)

    tasks_in_db = manager_json.load_data()

    expected_data = [task1_in_dict, task2_in_dict]

    assert expected_data == tasks_in_db, "Ожидаемые результаты отличаются!"

def test_edit_task(manager_json: TaskManagerJSON, tasks):
    old_task1, old_task2 = tasks

    modified_task1 = Task(
        id=1,
        title="Эта задача изменена",
        description="Описание тоже",
        category="Категория изменена",
        deadline=old_task1.deadline, # Сроки оставляем как было
        priority="Средний",
        status=False
    )

    manager_json.edit_task(old_task1, "title", modified_task1.title)
    manager_json.edit_task(old_task1, "description", modified_task1.description)
    manager_json.edit_task(old_task1, "category", modified_task1.category)
    manager_json.edit_task(old_task1, "priority", modified_task1.priority)

    tasks[0] = modified_task1

    tasks_in_db = manager_json.load_data()
    task1_in_db = tasks_in_db[0]

    expected_task1 = {
        "id": modified_task1.id,
        "title": modified_task1.title,
        "description": modified_task1.description,
        "category": modified_task1.category,
        "deadline": modified_task1.deadline,
        "priority": modified_task1.priority,
        "status": modified_task1.status,
    }
    assert task1_in_db == expected_task1, "Задача в базе данных не соответствует ожидаемому состоянию"

def test_get_cats(manager_json: TaskManagerJSON, tasks):
    task1, task2 = tasks

    cat_with_tasks = manager_json.get_cats()
    tasks_in_cat = cat_with_tasks.get("тесты")

    print(asdict(task2),  tasks_in_cat[0])

    assert len(tasks_in_cat) == 1, "Одна задача должна быть в категории"
    assert task2 == tasks_in_cat[0], "Ожидаемое, отличается от результата!"


def test_get_tasks(manager_json: TaskManagerJSON, tasks):
    tasks_in_db = manager_json.get_tasks()
    assert tasks_in_db == tasks


def test_complete_task(manager_json: TaskManagerJSON, tasks):
    task1, task2 = tasks
    manager_json.complete_task(task1)

    tasks_in_db = manager_json.load_data()
    task_in_db = tasks_in_db[0]

    task1.status = True
    tasks[0] = task1

    assert task_in_db.get("status") is True, "Статус задачи должен был измениться!"

def test_incomplete_task(manager_json: TaskManagerJSON, tasks):
    task1, task2 = tasks
    manager_json.incomplete_task(task1)

    tasks_in_db = manager_json.load_data()
    task_in_db = tasks_in_db[0]

    task1.status = False
    tasks[0] = task1

    assert task_in_db.get("status") is False, "Статус задачи должен был измениться!"


def test_find_to_entry_title(manager_json: TaskManagerJSON, tasks):
    string_for_search = "задач"
    lst_entry = manager_json.find_to_entry_title(string_for_search)
    assert tasks == lst_entry


def test_find_by_id(manager_json: TaskManagerJSON, tasks):
    task1, task2 = tasks

    tasks_in_db = manager_json.load_data()
    idx = manager_json.find_by_id(tasks_in_db, task1.id)
    assert tasks_in_db[idx] == asdict(task1)


def test_remove_task(manager_json: TaskManagerJSON, tasks):
    task1, task2 = tasks

    manager_json.remove_task(task2.id)
    tasks_in_db = manager_json.load_data()
    tasks.pop()

    assert asdict(task2) not in tasks_in_db, "Задача должна быть удалена"
    assert len(tasks_in_db) == len(tasks)

