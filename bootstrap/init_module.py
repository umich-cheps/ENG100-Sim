import logging
from simu_core import SimuCore

logger = logging.getLogger(__name__)


class InitModule:
    """
    Initializes the simulation infrastructure of the SimuCore 
    library.
    """

    def __init__(self, sim_core: SimuCore):
        self.sim_core = sim_core

    def execute(self):
        logger.debug("Running init module")
        print("Initializing simulation infrastructure...")
