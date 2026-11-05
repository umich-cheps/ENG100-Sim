from abc import ABC, abstractmethod
from collections import defaultdict
import logging
from enum import Enum
from .metrics_table import MetricsTable
from .statistics_table import StatisticsTable
logger = logging.getLogger(__name__)

class SimuCore(ABC):
    """Abstract base class for core simulation functionality.
    
    This class defines the methods for a simulation framework, 
    including event and task management, input handling, and
    report generation. It is designed to be subclassed for specific
    simulation implementations.

    Attributes:
        persistent_data (dict): A dictionary to store persistent data 
            across simulation runs.
    """
    event_type_stopping_criteria = {}
    event_random_variables = {}
    task_information_dict = {}

    class TaskBase:
        def __init__(self, task_type, epoch_id_due):
            self.task_type = task_type
            self.epoch_id_due = epoch_id_due

    def __init__(self, eventType: Enum, taskType: Enum):
        """Initialize an instance of SimuCore with event and task types.
        
        Args:
            eventType (Enum)
            taskType (Enum)

        Raises:
            TypeError: If eventType or taskType is not a subclass of 
                Enum.
        """
        
        self.NUM_WORKERS = 16
        self.persistent_data = {}
        self.process_function_names = {}
        self.event_types_stopping_criteria = {}
        self.event_random_variables = {}
        self.pending_events = {}
        self.task_list = defaultdict(list)
        self.update_metric_function_names = {}
        self.metrics_table = MetricsTable()
        self.simulation_statistics = StatisticsTable()
        
        # additions for efficiency purposes
        self.epochID = 0
        self.eventID = 0
        logging.basicConfig(
            filename="data/output/debug/log.txt",
            format='%(asctime)s %(levelname)s: %(name)s - %(message)s',
            datefmt='%H:%M:%S')
        logging.getLogger().setLevel(logging.WARNING)
        logging.getLogger('simulations').setLevel(logging.DEBUG)
        logging.getLogger('bootstrap').setLevel(logging.DEBUG)

        if not isinstance(eventType, type) or not issubclass(eventType, Enum):
            raise TypeError(f"{eventType} must be a subclass of Enum")
        
        if not isinstance(taskType, type) or not issubclass(taskType, Enum):
            raise TypeError(f"{taskType} must be a subclass of Enum")

    @abstractmethod
    def read_input(self):
        pass

    @abstractmethod
    def validate_input(self):
        pass

    def custom_simulation_stopping_criteria_met(self):
        raise RuntimeError("Custom simulation stopping criteria selected but not implemented")
    
    def custom_replication_stopping_criteria_met(self):
        raise RuntimeError("Custom replication stopping criteria selected but not implemented")

    @abstractmethod
    def task_comparator(self, a, b):
        return 1

    @abstractmethod
    def generate_reports(self):
        pass

    def custom_parsing(self):
        pass

    def init_epoch(self):
        pass
    
    def init_replication(self):
        pass