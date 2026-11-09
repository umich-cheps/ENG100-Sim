import traceback
import logging
import numpy as np

from simulations import ENG100
from bootstrap import ReadModule, InitModule, RunSimulationModule, GenSimMetricsModule, ReportModule, ParseModule
from simu_core.utils import log_errors

logger = logging.getLogger(__name__)

@log_errors
def run_simulation():
    sim_core = ENG100()

    gen_params_path = "data/input/eng_100/gen_params.txt"

    modules = [
        ReadModule(sim_core, gen_params_path), 
        ParseModule(sim_core),
        InitModule(sim_core),
        RunSimulationModule(sim_core),
        GenSimMetricsModule(sim_core),
        ReportModule(sim_core)
    ]

    for module in modules:
        module.execute()

if __name__ == "__main__":
    run_simulation() 
