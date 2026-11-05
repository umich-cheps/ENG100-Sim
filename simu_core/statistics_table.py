import logging
from typing import Any

from .base_table import BaseTable
from .database.repositories.statistics_repository import StatisticsRepository
from .database.models.simulation import Statistic

logger = logging.getLogger(__name__)

class StatisticsTable(BaseTable):

    # Override repository for metrics-specific operations
    repository: StatisticsRepository = StatisticsRepository()
    model: Any = Statistic

    def add_statistic(self, stat):
        if isinstance(stat, Statistic):
            stat = [stat]
        if not isinstance(stat, list):
            raise TypeError("Statistics must be passed in as list of Statistics objects")
 
        # Add to database
        for e in stat:
            self.repository.create(e)
