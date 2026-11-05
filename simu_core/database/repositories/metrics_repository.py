from pathlib import Path
from .base_repository import BaseRepository
from ..models.simulation import Metric
from typing import List, Optional, Dict, Any, Type
from pydantic import BaseModel

class MetricsRepository(BaseRepository):
    model: Type[BaseModel] = Metric
    tablename: str = "metrics"

    def __init__(self, **data):
        super().__init__(**data)

        # Create SQL table via inherited constrcutor
        with open(Path.cwd() / "sql" / "metrics.sql", "r") as f:
            self._build_table(f.read())
