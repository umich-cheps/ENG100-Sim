from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import ClassVar
import threading

class Metric(BaseModel):
    _counter: ClassVar[int] = 0
    _lock: ClassVar[threading.Lock] = threading.Lock()

    model_config = ConfigDict(extra="forbid")

    id: int = Field(default=None)
    replication_id: int | None = Field(default=None)
    percent_high_capacity_used: float | None = Field(default=None)
    percent_gen_capacity_used: float | None = Field(default=None)
    percent_gen_capacity_used_by_high: float | None = Field(default=None)
    percent_gen_capacity_used_by_low: float | None = Field(default=None)
    average_wait_time: float | None = Field(default=None)
    average_high_priority_wait_time: float | None = Field(default=None)
    average_low_priority_wait_time: float | None = Field(default=None)
    max_overall_wait_time: float | None = Field(default=None)
    max_high_priority_wait_time: float | None = Field(default=None)
    max_low_priority_wait_time: float | None = Field(default=None)

    @model_validator(mode="after")
    def assign_id(self):
        # if self.id is None:
        with type(self)._lock:
            type(self)._counter += 1
            self.id = type(self)._counter
        return self

class Statistic(BaseModel):
    _counter: ClassVar[int] = 0
    _lock: ClassVar[threading.Lock] = threading.Lock()

    model_config = ConfigDict(extra="forbid")

    id: int = Field(default=None)
    metric_name: str = Field(default=None)
    mean: float | None= Field(default=None)
    median: float | None= Field(default=None)
    ci_low: float | None= Field(default=None)
    ci_high: float | None= Field(default=None)

    @model_validator(mode="after")
    def assign_id(self):
        # if self.id is None:
        with type(self)._lock:
            type(self)._counter += 1
            self.id = type(self)._counter
        return self
