# Менеджер задач

## 🌍 Обзор
Консольное приложение для управления задачами, которое помогает пользователям эффективно организовывать свои дела. Этот проект является тестовым заданием, демонстрирующим основные функции для создания, управления и поиска задач.

## 🧬 Возможности

### 1. Просмотр задач
- Просмотр всех текущих задач.
- Фильтрация задач по категориям (например, Работа, Личное, Обучение).

### 2. Добавление задач
- Добавление новых задач с указанием следующих данных:
  - **Название**
  - **Описание**
  - **Категория**
  - **Срок выполнения**
  - **Приоритет** (Низкий, Средний, Высокий)

### 3. Редактирование задач
- Изменение деталей существующих задач.
- Отметка задач как выполненных.

### 4. Удаление задач
- Удаление задач по уникальному идентификатору или категории.

### 5. Поиск задач
- Поиск задач по ключевым словам, категории или статусу выполнения.


### Функциональные моменты
- **Командный интерфейс (CLI)**: Приложение работает исключительно через консоль без графического или веб-интерфейсов. Но при этом разделение логики и отображение позволяют с легкостью перейти на определенный интерфейс.
- **Хранение данных**:
  - Задачи хранятся в формате **JSON** или **CSV**.
  - Каждая задача имеет уникальный идентификатор.
- **Поля задачи**:
  - Название
  - Описание
  - Категория
  - Срок выполнения
  - Приоритет (Низкий, Средний, Высокий)
  - Статус (Выполнена/Не выполнена)

### Нефункциональные моменты
1. **Обработка ошибок**:
   - Корректная обработка некорректного ввода, например, неправильных дат или пустых полей.
2. **Тестирование**:
   - Обеспечение надежного тестирования всех основных функций с использованием `pytest`.

## 🧐 Технологический стек

| Компонент            | Технология         |
|----------------------|--------------------|
| Консольный интерфейс | [rich](https://rich.readthedocs.io/) |
| Фреймворк для тестов | [pytest](https://docs.pytest.org/)  |
| Отчетность по тестам | [pytest-coverage](https://pytest-cov.readthedocs.io/) |

## 🖌️ Установка и настройка

1. **Клонирование репозитория**:
   ```bash
   git clone https://github.com/zalimpshigotizhev/task_cli.git
   cd task_cli
   ```

2. **Создание виртуального окружения** (опционально):
   ```bash
   poetry shell
   ```


## ⚙️ Использование

### Запуск приложения
```bash
python main.py
```



## 🔧 Тестирование

1. **Запуск тестов**:
   ```bash
   pytest
   ```

2. **Генерация отчета о покрытии тестами**:
   ```bash
   pytest --cov=tasks
   ```

## ✉ Обратная связь
Вы можете оставить свои предложения или сообщить об ошибках через [GitHub Issues](https://github.com/zalimpshigotizhev/task_cli/issues).
