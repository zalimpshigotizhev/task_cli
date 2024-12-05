from rich.console import Console
from rich.text import Text

from utils.funcs import make_panel, choices_options

from utils import const
from tasks.views import TaskCLI


class Menu:
    def __init__(self):
        self.console = Console()
        self.task_cli = TaskCLI()
        self.nav_comm = Text.assemble((const.GREY_MAKE_A_CHOICE, "bold grey42"))
        self.options = {
            "1": ("Список задач", self.task_cli.get_tasks),
            "2": ("Добавить новую задачу", self.task_cli.add_task),
            "3": ("Найти задачу", self.task_cli.search_task)
        }

    def start(self) -> None:
        """
        Начало.
        На данном этапе происходит вывод опций
        на главном экране.
        """
        self.console.clear()
        group_choices = choices_options(self.options)

        self.console.print(
            make_panel(
                self.nav_comm, *group_choices,
                title="Добро пожаловать!"
            )
        )


    def distribute(self, selected: str) -> None:
        """
        Распределитель функций, смотря какой
        будет `selected` вызывается опция из
        self.option.
        Он также отвечает за `nav_comm` внутри объекта.
        :param selected:
        """
        action = self.options.get(selected)
        if action:
            _, func = action
            func()
            self.nav_comm = Text.assemble((const.GREY_MAKE_A_CHOICE, "bold grey42"))
        else:
            self.nav_comm = Text.assemble((const.RED_MAKE_A_CHOICE, "bold red1"))
