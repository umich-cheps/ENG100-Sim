import logging
from typing import Any, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class BaseTable(BaseModel):
    db : Any = None
    repository : Any = None
    ID: int = 0
    model: Any = None
    to_flush: List = []

    def __init__(self, **data):
        super().__init__(**data)
    
    def get_all(self):
        return self.repository.get_all()
    
    def get_by_id(self, id):
        return self.repository.get_by_id(id)
    
    def get_by_column_value(self, column, value):
        return self.repository.get_by_column_value(column, value)
    
    def add(self, item, flush=True):
        if not self.repository.model:
            raise ValueError(f"Repository's model attribute must be defined")
        if isinstance(item, self.model):
            item = [item]
        if not isinstance(item, list):
            raise TypeError(f"Items must be passed in as list of {self.model} objects")
        
        for e in item:
            if not isinstance(e, self.model):
                raise TypeError(f"All items must be {self.model.__name__} objects")
            
        # Add to database
        if flush and len(item) == 1:
            self.repository.create(item[0])
        else:
            for e in item:
                self.to_flush.append(e)
            if flush:
                self.flush()
    
    def update_column_values(self, col_name, old_value, new_value, num_rows=-1):
        return self.repository.update_column(col_name, old_value, new_value, num_rows)
    
    def conditional_update_column_values(self, condition_col, condition_value, update_col, new_value):
        return self.repository.conditional_update_column(condition_col, condition_value, update_col, new_value)
    
    def read_query(self, statement):
        return self.repository.execute_query(statement)
    
    def flush(self):
        if self.to_flush:
            self.repository.bulk_insert(self.to_flush)
            self.to_flush = []
    