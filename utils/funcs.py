import time

from rich.console import Group
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from tasks.models import Task


def get_time() -> str:
    """
    :return: Возвращает текущее время
    """
    return time.strftime("%H:%M")


def make_panel(
        *notes: str | Text | tuple[str, str | Style] | Task,
        title: str | None = None,
        subtitle: bool = True
) -> Panel:
    """
    Создает и возвращает объект `rich.Panel`
    рамка в которой находится каждый ответ на запрос.

    :param notes: Один или несколько записей. Содержимое.
    :param title: Название контекста в котором находимся.
    :param subtitle: Показывать ли текущее время снизу.
    :return: Возвращает панель.
    """
    if title:
        title = Text.assemble((title, "bold sky_blue3"))

    curr_time = Text.assemble((get_time(), "bold sky_blue3"))
    panel = Panel(
        Group(*notes),
        title=title, subtitle=curr_time if subtitle else None
    )
    return panel


def choices_options(
        options: dict,
) -> list[Text]:
    """
    Раскидывает словарь с опциями на
    `<код>. <описание действие>`.
    :param options: Словарь с опциями.
    :return: Возвращает список с объектом `rich.Text`
    """
    repr_options = []
    for choice, option in options.items():
        title, _ = option
        repr_options.append(Text.assemble(
            (f"{choice}. ", "bold bright_black"),
            title
        ))
    return repr_options


