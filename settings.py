from dataclasses import dataclass
import os


@dataclass
class SETTINGS:
    limited: int = 6
    base_dir: str = os.path.dirname(os.path.abspath(__file__))
    path_db: str = os.path.join(base_dir, "db", "data.json")
    path_auto_incr: str = os.path.join(base_dir, "db", "auto_increment_tasks.txt")


settings = SETTINGS()
