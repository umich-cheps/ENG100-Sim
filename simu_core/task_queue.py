import heapq
from functools import cmp_to_key
from typing import Callable, Any
from enum import IntEnum
from pydantic import BaseModel


class ComparatorValues(IntEnum):
    """Enum for comparator return values.
    
    This enum is used to enforce that the comparator function
    returns one of the three values: -1, 0, or 1.
    """
    HIGHER_PRIORITY = 1
    LOWER_PRIORITY = -1
    EQUAL_PRIORITY = 0


class TaskQueue():
    comparator: Callable[[dict, dict], int] | None = None
    key: Any = None
    pq: list = []

    def __init__(self, sort_func: Callable[[dict, dict], int], **data):
        """Initialize the task queue with a custom sorting function.

        Args:
            sort_func (Callable[[dict, dict], int]): A function that 
                compares two task dictionaries and returns an integer 
                indicating their priority. The function should use the 
                ComparatorValues enum to determine the integer.
        """
        self.comparator = sort_func
        # self.key = cmp_to_key(self.comparator)
        super().__init__(**data)

    def add_tasks_to_queue(self, tasks_to_complete: list):
        for task in tasks_to_complete:
            heapq.heappush(self.pq, (cmp_to_key(self.comparator)(task), task.id, task))

    def get_next_task(self):
        return heapq.heappop(self.pq)[2]

    def empty(self):
        return len(self.pq) == 0

    def clear(self):
        self.pq = []
