import logging
import math
import statistics
import duckdb
from simu_core import SimuCore
from simu_core import Statistic
from sqlalchemy import inspect, func



logger = logging.getLogger(__name__)


class GenSimMetricsModule:
    """Generate simulation metrics after the simulation has completed."""

    def __init__(self, sim_core: SimuCore):
        self.sim_core = sim_core

    def execute(self):
        """Generate simulation metrics."""
        logger.debug("Running GenSimMetricsModule")
        print("Generating simulation metrics...")
        self.calculate_statistics()
        metrics = self.sim_core.metrics_table.get_all()
        logger.debug("Printing simulation metrics")
        logger.info("Metrics: %s", "\n".join(str(metric) for metric in metrics))
    
    def calculate_statistics(self):
        """
        Calculate the mean, median, and 95% CI for each metric
        """
        conn = duckdb.connect(":memory:shared")
        try:
            for metric in self.sim_core.update_metric_function_names:

                # Gather column values to use statistics
                raw_col_values = [v[0] for v in conn.execute(f"SELECT {metric} FROM metrics;").fetchall()]
                col_values = [float(v) for v in raw_col_values if v is not None]
                n = len(col_values)
                if n > 1:
                    median = statistics.median(col_values)
                    mean = statistics.mean(col_values)
                    stdev = statistics.stdev(col_values)

                    # Calculate 95% CI
                    standard_error = stdev / math.sqrt(n)
                    ci_low = mean - 1.96 * standard_error
                    ci_high = mean + 1.96 * standard_error
                
                else:
                    median = None
                    mean = None
                    ci_low = None
                    ci_high = None
                curr_statistics = Statistic()
                setattr(curr_statistics, "metric_name", metric)
                setattr(curr_statistics, "mean", mean)
                setattr(curr_statistics, "median", median)
                setattr(curr_statistics, "ci_low", ci_low)
                setattr(curr_statistics, "ci_high", ci_high)

                self.sim_core.simulation_statistics.add_statistic(curr_statistics)
        finally:
            conn.close()

