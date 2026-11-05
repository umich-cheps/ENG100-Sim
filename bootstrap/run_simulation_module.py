import time
import logging
import math
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from functools import cmp_to_key
from simu_core import TaskQueue
from simu_core import SimuCore
from simu_core import FunctionNotFoundError
from simu_core import Metric

logger = logging.getLogger(__name__)


class RunSimulationModule:
    """Runs the simulation model using the SimuCore library."""

    def __init__(self, sim_core: SimuCore):
        self.sim_core = sim_core

    def execute(self):
        logger.debug("Running RunSimulationModule")
        print("Running simulation...")

        self.sim_core.execution_start_time = time.time()

        def run_loop(sim_core, replicationID):
            sim_core.init_replication()
            # Epoch/IGW loop
            sim_core.epochID = 0
            while not self.replication_stopping_criteria_met(sim_core.epochID):
                sim_core.init_epoch()
                epoch_events = self.gen_events(sim_core, replicationID)
                self.process_events(sim_core, epoch_events)

                # Get tasks due for current epoch and add to task_queue
                #task_for_epoch = sim_core.task_table.get_by_epoch_and_replication_created(sim_core.epochID, replicationID)

                # Sort tasks based on user-defined comparator
                #sim_core.task_queue.add_tasks_to_queue(task_for_epoch)

                # Only sort if there is more than one task in the task list for the current epoch
                # If there is only one element or 0 elements, there is no need to sort
                if len(sim_core.task_list[sim_core.epochID]) > 1:
                    self.sort_tasks(sim_core, sim_core.epochID)
                 
                self.do_tasks(sim_core, sim_core.epochID)

                # sim_core.task_queue.clear()
                # sim_core.task_table.increment_epoch()
                sim_core.epochID += 1

            # At the end of each epoch, generate replication metrics
            self.update_metrics(sim_core, replicationID)

            # Reset tables and clear tasks for the next replication
            # sim_core.reset()
            # sim_core.task_table.clear()
            # sim_core.eventID = 0

            # Increment replication counter
            # self.sim_core.task_table.increment_replication()

        # replicationID = 0
        # while not self.simulation_stopping_criteria_met(replicationID):
        #     run_loop(deepcopy(self.sim_core), replicationID)
        #     replicationID += 1


        # Replication loop
        replicationID = 0
        pending = set()
        with ThreadPoolExecutor(max_workers=self.sim_core.NUM_WORKERS) as executor:
            while not self.simulation_stopping_criteria_met(replicationID):
                while len(pending) < self.sim_core.NUM_WORKERS and not self.simulation_stopping_criteria_met(replicationID):
                    future = executor.submit(run_loop, deepcopy(self.sim_core), replicationID)
                    replicationID += 1
                    pending.add(future)

                    if not pending:
                        break

                    _, pending = wait(pending, return_when=FIRST_COMPLETED)
            wait(pending)

    def replication_stopping_criteria_met(self, epochID):
        """Check if the replication stopping criteria is met.

        Replication stopping criteria can be based on:
            - Number of epochs
            - Custom criteria defined by the tool developer
        
        Returns:
            bool: True if stopping criteria is met, False otherwise.
        
        Raises:
            ValueError: If the replication stopping criteria is not recognized.
        """
        if self.sim_core.replication_stopping_criteria == "num_epochs":
            return (epochID >= self.sim_core.replication_stopping_threshold)

        if self.sim_core.replication_stopping_criteria == "custom":
            return self.sim_core.custom_replication_stopping_criteria_met()
        
        raise ValueError(
            "Replication stopping criteria not recognized, "
            "options include {'num_epochs', 'custom'}")

    def simulation_stopping_criteria_met(self, replicationID):
        """Check if the simulation stopping criteria is met.
        
        Stopping criteria can be based on:
            - Number of replications
            - Execution time
            - Custom criteria defined by the user

        Returns:
            bool: True if stopping criteria is met, False otherwise.

        Raises:
            ValueError: If the simulation stopping criteria is not 
                recognized.
        """
        if self.sim_core.simulation_stopping_criteria == "num_replications":
            return (replicationID >= self.sim_core.simulation_stopping_threshold)

        # Check if execution time in seconds is less than the threshold 
        if self.sim_core.simulation_stopping_criteria == "execution_time":
            return ((time.time() - self.sim_core.execution_start_time)
                        >= self.sim_core.simulation_stopping_threshold)

        if self.sim_core.simulation_stopping_criteria == "custom":
            return self.sim_core.custom_simulation_stopping_criteria_met()

        raise ValueError(
            "Simulation stopping criteria not recognized, "
            "options include {'num_replications', 'execution_time', 'custom'}")
    
    def simulation_to_epoch_time_units(self, sim_core, simulation_time):
        return simulation_time / sim_core.epoch_duration
    
    def epoch_to_simulation_time_units(self, sim_core, epoch_time):
        return epoch_time * sim_core.epoch_duration
    

    def gen_events(self, sim_core, replicationID):
        """
        Generate a single epoch's worth of events for all event types
        """
        events = []
        for e in sim_core.event_random_variables:
            clock = 0.0
            if (sim_core.event_type_stopping_criteria[e]["stopping_criteria"] == "interarrival"):
                if (e in sim_core.pending_events):
                    if (math.floor(sim_core.pending_events[e]) > sim_core.epochID):
                        continue # Do not generate events of this type for this epoch
                    epoch_time_clock_start = sim_core.pending_events[e] - sim_core.epochID
                    clock = self.epoch_to_simulation_time_units(sim_core, epoch_time_clock_start)

                    # Add the pending event to the event list
                    events.append({
                    "replication_id": replicationID,
                    "epoch_id_created": sim_core.epochID,
                    "event_type": e,
                    "outcome": clock,
                    "id": sim_core.eventID
                    })
                    sim_core.eventID += 1
                else: # If there is no pending event for this event type
                    clock = 0.0
            count = 0
            while (not self.event_generation_stopping_criteria_met(sim_core, e, clock, count)):
                rv = sim_core.event_random_variables[e]
                event_outcome = float(rv.sample(1)[0])
                clock += event_outcome

                events.append({
                    "replication_id": replicationID,
                    "epoch_id_created": sim_core.epochID,
                    "event_type": e,
                    "outcome": clock,
                    "id": sim_core.eventID
                })
                sim_core.eventID += 1
                count += 1
            # If an interarrival, update pending events since 
            # it will exceeed the end of the epoch
            # Note that the event that will exceed the epoch should be added to the events list
            # of the epoch it was created.
            if (sim_core.event_type_stopping_criteria[e]["stopping_criteria"] == "interarrival"):
                sim_core.pending_events[e] = self.simulation_to_epoch_time_units(sim_core, clock) + sim_core.epochID
                events.pop() # We pop the "overflow" event, since it will be reported at the beginning of the epoch it occurs in
        return events

    def event_generation_stopping_criteria_met(self, sim_core, event_type_name, clock, count):
        """
        Handles event generation stopping criteria for a given event 
        type.

        Args:
            event_type_name (str): The name of the event type 
                (e.g., "student_arrival").
            clock (float): Current clock time for interarrival event 
                types.
            count (int): Current count of occurrences for number of trials trial-based 
                event types.

        Returns:
            bool: True if stopping criteria is met, False otherwise.

        Raises:
            ValueError: If the event type or its stopping criteria is 
                not recognized.
        """
        event_type_params = sim_core.event_params_dict.get(event_type_name)
        if event_type_params is None:
            raise ValueError(f"Event type '{event_type_name}' not recognized.")

        stopping_criteria = event_type_params.get("stopping_criteria")

        if stopping_criteria == "interarrival":
            return clock >= sim_core.epoch_duration
        elif stopping_criteria == "num_trials":
            return count >= event_type_params.get("threshold")
        else:
            raise ValueError(
                "Event generation stopping criteria not recognized, "
                "options include {'interarrival', 'num_trials'}")
    
    def process_events(self, sim_core, current_epoch_events):
        """
        Process all events from the current epoch

        Returns: 
            Nothing

        Raises:
            FunctionNotFoundError: If any event_type does not have a
                corresponding handling function
        """
        for event in current_epoch_events:
            event_type = sim_core.EventTypes(event["event_type"])
            if not event_type in sim_core.process_function_names:
                raise FunctionNotFoundError(f"{event.event_type} does not have a defined process function in the process_function_names dict.")
            
            sim_core.process_function_names[event_type](event)
    
    def sort_tasks(self, sim_core, epochID):
        """Sort the tasks for the given epoch"""
        sim_core.task_list[epochID].sort(key=cmp_to_key(sim_core.task_comparator))

        
    def do_tasks(self, sim_core, epochID):
        """
        Do all tasks due at the given epoch
        Deletes the tasks at the given epoch after they have been completed

        Returns:
            Nothing
        
        Raises:
            FunctionNotFoundError: If any task_type does not have a corresponding
                handling function
        """
        curr_epoch_tasks = sim_core.task_list[epochID]
        for i in range(len(curr_epoch_tasks)):
            curr_task = curr_epoch_tasks[i]
            sim_core.task_type_information_dict[
                sim_core.TaskTypes(curr_task.task_type)]['do_task_type_function_name'](curr_task)
        sim_core.task_list.pop(epochID)
        
    def update_metrics(self, sim_core, replicationID):
        """
        Update metrics table according to the current replication

        Returns:
            Nothing
        
        Raises:
            None
        """
        curr_metrics = Metric()
        for metric in sim_core.update_metric_function_names:
            setattr(curr_metrics, metric, sim_core.update_metric_function_names[metric]())
            setattr(curr_metrics, "replication_id", replicationID)
        sim_core.metrics_table.add_metric(curr_metrics)
        


