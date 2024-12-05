import os


class ManagerID:
    """Класс для работы с ID объектов универсальный
    в основном используется для автоматического инкремента.
    """
    def __init__(self, path: str) -> None:
        """
        :param path: Принимает путь, где находится файл с последним ID
        """
        self.path = path

        if not os.path.exists(self.path):
            # Если файл не существует, создаем его с пустым списком задач
            with open(self.path, 'w', encoding='utf-8') as file:
                file.write("1")

    def load_id(self) -> int:
        """Получает последний ID"""
        with open(self.path, 'r', encoding='utf-8') as file:
            id = file.read()

        if (not id
                or not id.isdigit()):
            return 1
        return int(id)

    def update_id(self, new_id: int) -> int:
        """Сохраняет новое значение"""
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(str(new_id))
        return new_id

    def increment(self) -> int:
        """Увеличивает значение на одну"""
        curr_id = self.load_id()
        new_id = self.update_id(curr_id + 1)
        return new_id
