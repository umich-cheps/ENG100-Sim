import logging
from typing import Any
from pydantic import Field

from .base_table import BaseTable
from .database.repositories.metrics_repository import MetricsRepository
from .database.models.simulation import Metric

logger = logging.getLogger(__name__)

class MetricsTable(BaseTable):

    # Override repository for metrics-specific operations
    repository: MetricsRepository = Field(default_factory=MetricsRepository)
    model: type[Metric] = Metric
    
    def get_by_replication(self, rep_num):
        return self.repository.get_by_replication(rep_num)
    
    def add_metric(self, metric):
        if isinstance(metric, Metric):
            metric = [metric]
        if not isinstance(metric, list):
            raise TypeError("Metrics must be passed in as list of Metrics objects")
            
        # Add to database
        for e in metric:
            self.repository.create(e)
