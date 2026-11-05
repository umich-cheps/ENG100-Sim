from pathlib import Path
from .base_repository import BaseRepository
from ..models.simulation import Statistic
from typing import List, Optional, Dict, Any, Type
from pydantic import BaseModel

class StatisticsRepository(BaseRepository):
    model: Type[BaseModel] = Statistic
    tablename: str = "statistics"

    def __init__(self, **data):
        super().__init__(**data)

        # Create SQL table via inherited constrcutor
        with open(Path.cwd() / "sql" / "statistics.sql", "r") as f:
            self._build_table(f.read())
