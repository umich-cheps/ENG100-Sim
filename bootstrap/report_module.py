import logging
from simu_core import SimuCore

logger = logging.getLogger(__name__)


class ReportModule:
    """Generate reports after the simulation has run."""

    def __init__(self, sim_core: SimuCore):
        self.sim_core = sim_core

    def execute(self):
        self.sim_core.generate_reports()
