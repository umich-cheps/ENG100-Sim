import logging
import heapq
import random
from enum import Enum
from simu_core import SimuCore
from simu_core import FileUtil
from simu_core import RandomVariable
from simu_core import ComparatorValues
from simu_core import MetricsTable

logger = logging.getLogger(__name__)

class ENG100(SimuCore):
    class EventTypes(Enum):
        LO_PRIORITY = 0
        HI_PRIORITY = 1

    class TaskTypes(Enum):
        SCHEDULE_PT = 0
    
    class Task(SimuCore.TaskBase):
        def __init__(self, task_type, epoch_id_due, priority):
            super().__init__(task_type, epoch_id_due)
            self.priority = priority # priority = 1 if pt is hi, otherwise priority = 0


    def __init__(self):
        super().__init__(self.EventTypes, self.TaskTypes)
        self.file_util = FileUtil()
        self.process_function_names = {self.EventTypes.HI_PRIORITY: self.process_hi_priority_event,
                                       self.EventTypes.LO_PRIORITY: self.process_lo_priority_event,}
        self.task_type_information_dict = {self.TaskTypes.SCHEDULE_PT:
                                      {'do_task_type_function_name': self.do_task_type_schedule_patient}}
        self.update_metric_function_names = {"percent_high_capacity_used": self.update_percent_high_cap_used_metric,
                                             "percent_gen_capacity_used": self.update_percent_gen_cap_used_metric,
                                             "percent_gen_capacity_used_by_high": self.update_percent_gen_cap_used_by_high_metric,
                                             "percent_gen_capacity_used_by_low": self.update_percent_gen_cap_used_by_low_metric,
                                             "average_wait_time": self.update_average_wait_time_metric,
                                             "average_high_priority_wait_time": self.update_average_high_priority_wait_time_metric,
                                             "average_low_priority_wait_time": self.update_average_low_priority_wait_time_metric,
                                             "max_overall_wait_time": self.update_max_overall_wait_time_metric,
                                             "max_high_priority_wait_time": self.update_max_high_priority_wait_time,
                                             "max_low_priority_wait_time": self.update_max_low_priority_wait_time}

    def read_input(self):
        print("Reading input...")
        self.patient_sort_style = self.cust_params_dict['patient_sort_style'].lower()
        self.num_hi_appts = int(self.cust_params_dict['num_high_priority_appointments'])
        self.num_gen_appts = int(self.cust_params_dict['num_general_priority_appointments'])
        self.num_epochs = self.gen_params_dict['num_epochs']
   
    def validate_input(self):
        if not (self.patient_sort_style == "random" or 
               self.patient_sort_style == "hi_first" or self.patient_sort_style == "lo_first"):
            print("invalid sort type")
            exit(1)
        if not (self.num_hi_appts >= 0):
            print("number of high priority appointments must be non-negative")
            exit(1)
        if not (self.num_gen_appts >= 0):
            print("number of general priority appointments must be non-negative")
            exit(1)
        if not (self.event_params_dict[self.EventTypes.HI_PRIORITY]['distribution'] == 'uniform'):
            print("High priority patient distribution type must be uniform")
            exit(1)
        if not (self.event_params_dict[self.EventTypes.LO_PRIORITY]['distribution'] == 'uniform'):
            print("High priority patient distribution type must be uniform")
            exit(1)
        if not ((self.event_params_dict[self.EventTypes.LO_PRIORITY]['upper_bound'] - 
                            self.event_params_dict[self.EventTypes.LO_PRIORITY]['upper_bound'])%2 ==0):
            print("The difference between LO_PRIORITY distribution upper_bound and lower_bound must be even")
            exit(1)
        if not ((self.event_params_dict[self.EventTypes.HI_PRIORITY]['upper_bound'] - 
                            self.event_params_dict[self.EventTypes.HI_PRIORITY]['upper_bound'])%2 ==0):
            print("The difference between HI_PRIORITY distribution upper_bound and lower_bound must be even")
            exit(1)
        self.event_random_variables[self.EventTypes.HI_PRIORITY].params['lower_bound'] -= 0.4999999
        self.event_random_variables[self.EventTypes.HI_PRIORITY].params['upper_bound'] += 0.4999999

    def init_replication(self):
        self.high_capacity_by_day = [self.num_hi_appts] * self.num_epochs
        self.gen_capacity_by_day = [self.num_gen_appts] *self.num_epochs
        self.next_avail_high = 0
        self.next_avail_gen = 0
        self.high_assigned_to_high = 0
        self.high_assigned_to_gen = 0
        self.low_assigned = 0
        self.max_high_wait_time = 0
        self.max_low_wait_time = 0
        self.total_high_wait_time = 0
        self.total_low_wait_time = 0
        self.high_pts_scheduled = 0
        self.low_pts_scheduled = 0
    
    def init_epoch(self):
        if self.next_avail_high < self.epochID:
            self.next_avail_high = self.epochID
        if self.next_avail_gen < self.epochID:
            self.next_avail_gen = self.epochID

    def process_hi_priority_event(self, event):
        num_pts = round(event["outcome"])
        for i in range (num_pts):
            task = self.Task(task_type=self.TaskTypes.SCHEDULE_PT, epoch_id_due=self.epochID, priority=1)
            self.task_list[self.epochID].append(task)

    def process_lo_priority_event(self, event):
        num_pts = round(event["outcome"])
        for i in range (num_pts):
            task = self.Task(task_type=self.TaskTypes.SCHEDULE_PT, epoch_id_due=self.epochID, priority=0)
            self.task_list[self.epochID].append(task)

    def task_comparator(self, a: Task, b: Task):
        if self.patient_sort_style == "random":
            random_a = random.random()
            random_b = random.random()
            if random_a < random_b:
                return 1
            elif random_b < random_a:
                return -1
            else:
                return 0
        elif self.patient_sort_style == "hi_first":
            if a.priority == b.priority:
                return 0
            elif a.priority: #priority is 1 if it is hi_priority
                return -1
            elif b.priority:
                return 1
            
        elif self.patient_sort_style == "lo_first":
            if a.priority == b.priority:
                return 0
            elif not a.priority: #priority is 1 if it is hi_priority
                return -1
            elif not b.priority:
                return 1


    def do_task_type_schedule_patient(self, task: Task):
        while (self.next_avail_gen < len(self.gen_capacity_by_day) and
               self.gen_capacity_by_day[self.next_avail_gen] == 0):
            self.next_avail_gen += 1

        if not task.priority: # if task is for a low priority patient
            if self.next_avail_gen < len(self.gen_capacity_by_day): # otherwise, the next available appointment is too far out
                self.gen_capacity_by_day[self.next_avail_gen] -=1
                self.low_assigned +=1
                self.max_low_wait_time = max(self.max_high_wait_time, self.next_avail_gen - task.epoch_id_due)
                self.total_low_wait_time += self.next_avail_gen - task.epoch_id_due
                self.low_pts_scheduled += 1

        else: # if task is for a high priority patient
            while (self.next_avail_high < len(self.high_capacity_by_day) and
                   self.high_capacity_by_day[self.next_avail_high] == 0):
                    self.next_avail_high += 1
            if (self.next_avail_gen < len(self.gen_capacity_by_day) or 
                                        self.next_avail_high < len(self.high_capacity_by_day)):
                if self.next_avail_gen < self.next_avail_high:
                    self.gen_capacity_by_day[self.next_avail_gen] -=1
                    self.high_assigned_to_gen += 1
                    self.max_high_wait_time = max(self.max_high_wait_time, self.next_avail_gen - task.epoch_id_due)
                    self.total_high_wait_time += self.next_avail_gen - task.epoch_id_due
                    self.high_pts_scheduled += 1
                else: 
                    self.high_capacity_by_day[self.next_avail_high] -=1
                    self.high_assigned_to_high +=1
                    self.max_high_wait_time = max(self.max_high_wait_time, self.next_avail_high - task.epoch_id_due)
                    self.total_high_wait_time += self.next_avail_high - task.epoch_id_due
                    self.high_pts_scheduled += 1

    def update_percent_high_cap_used_metric(self):
        return (self.high_assigned_to_high / (self.num_hi_appts * self.num_epochs))*100

    def update_percent_gen_cap_used_metric(self):
        return ((self.high_assigned_to_gen + self.low_assigned) / (self.num_gen_appts * self.num_epochs)) *100

    def update_percent_gen_cap_used_by_high_metric(self):
        return ((self.high_assigned_to_gen) / (self.num_gen_appts * self.num_epochs))*100

    def update_percent_gen_cap_used_by_low_metric(self):
        return (self.low_assigned / (self.num_gen_appts * self.num_epochs))*100

    def update_average_wait_time_metric(self):
        return (self.total_high_wait_time + self.total_low_wait_time) / (self.high_pts_scheduled + self.low_pts_scheduled)

    def update_average_high_priority_wait_time_metric(self):
        return (self.total_high_wait_time) / self.high_pts_scheduled

    def update_average_low_priority_wait_time_metric(self):
        return (self.total_low_wait_time) / self.low_pts_scheduled

    def update_max_overall_wait_time_metric(self):
        return max(self.max_high_wait_time, self.max_low_wait_time)

    def update_max_high_priority_wait_time(self):
        return self.max_high_wait_time

    def update_max_low_priority_wait_time(self):
        return self.max_low_wait_time

    def generate_reports(self):
        stats = self.simulation_statistics.get_all()
        for s in stats:
            name = getattr(s, "metric_name")
            mean = getattr(s, "mean")
            median = getattr(s,"median")
            ci_low = getattr(s, "ci_low")
            ci_high = getattr(s, "ci_high")
            print(f"Metrics name: {name}    mean: {mean:.2f}    median: {median:.2f}    95% confidence interval: ({ci_low:.2f}, {ci_high:.2f})")
