import duckdb
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ..models import *

class BaseRepository(BaseModel, ABC):
    # base classes need to set this
    model: Any = Field(default=None, description="Pydantic class type used to represent SQL records")
    tablename: str = Field(default=None, description="Name of internal SQL table")

    def _get_conn(self) -> duckdb.DuckDBPyConnection:
        """Return a new connection to the in-memory DB"""
        return duckdb.connect(":memory:shared")
    
    def _build_table(self, sql: str | None = None) -> None:
        """Create a new SQL table in the in-memory DB"""
        conn = self._get_conn()

        # Create the SQL table - SQLi safe
        if sql:
            conn.execute(sql)
            conn.commit()
            conn.close()
        conn = self._get_conn()
    
    def create(self, data: Any) -> Any:
        """Insert record(s) to the DB"""
        if not self.model:
            raise ValueError("self.model must be defined when calling any database functions")
        if not isinstance(data, self.model):
            raise TypeError(f"data must be of type {type(self.model)}")
        
        conn = self._get_conn()

        # Get keys/values of the record to be inserted
        dump = data.model_dump()

        columns = ', '.join([k for k in dump.keys()])
        placeholders = ", ".join((["?"] * len(dump)))

        # Build query - SQLi safe (parameterized - see placeholders definition)
        query = f"INSERT INTO {self.tablename} ({columns}) VALUES ({placeholders})"

        conn.execute(query, [v for v in dump.values()])
        conn.commit()
        return data
    
    def get_by_id(self, id: int) -> Optional[Any]:
        """Return a record that has a particular id"""
        if not self.model:
            raise ValueError("self.model must be defined when calling any database functions")
        
        conn = self._get_conn()
        tmp = conn.execute(f"SELECT * FROM {self.tablename} WHERE id = ?", (id,)).fetchone()

        if tmp is None:
            return None

        return self.model(**dict(zip(self.model.model_fields, tmp)))
    
    def get_all(self) -> List[Any]:
        """Return all records in the DB table"""
        if not self.model:
            raise ValueError("self.model must be defined when calling any database functions")
        
        conn = self._get_conn()
        tmp = conn.execute(f"SELECT * FROM {self.tablename}").fetchall()
        return [self.model(**dict(zip(self.model.model_fields, t))) for t in tmp]
    
    def get_by_epoch_and_replication(self, epoch: int, replication_id: int) -> List[Any]:
        """Return all records in a particular replication and epoch"""
        if not self.model:
            raise ValueError("self.model must be defined when calling any database functions")
        
        conn = self._get_conn()
        tmp = conn.execute(f"SELECT * FROM {self.tablename} WHERE replication_id = ? AND epoch_id_created = ?", (replication_id, epoch)).fetchall()
        return [self.model(**dict(zip(self.model.model_fields, t))) for t in tmp]
    
    def get_by_replication(self, replication_id: int) -> List[Any]:
        """Return all records that are in a particular replication"""
        if not self.model:
            raise ValueError("self.model must be defined when calling any database functions")
        
        conn = self._get_conn()
        tmp = conn.execute(f"SELECT * FROM {self.tablename} WHERE replication_id = ?", (replication_id,)).fetchall()
        return [self.model(**dict(zip(self.model.model_fields, t))) for t in tmp]
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[Any]:
        """Update a record in the repository's table. Returns update row"""
        if not self.model:
            raise ValueError("self.model must be defined when calling any database functions")
        
        conn = self._get_conn()
        placeholders = ", ".join([f"{k}=?" for k in data.keys()])
        conn.execute(f"UPDATE {self.tablename} SET {placeholders} WHERE id = ?", list(data.values()) + [id])
        conn.commit()
        tmp = conn.execute(f"SELECT * FROM {self.tablename} WHERE id = ?", (id,)).fetchone()
        return [self.model(**dict(zip(self.model.model_fields, t))) for t in tmp]
    
    def delete(self, id: int) -> bool:
        """Delete a record (selected by id) from the table. Return True if the record exists, False otherwise"""
        if not self.model:
            raise ValueError("self.model must be defined when calling any database functions")
        
        conn = self._get_conn()
        # Check that the record exists
        if conn.execute(f"SELECT * FROM {self.tablename} WHERE id = ?", (id,)).fetchone() == None:
            return False
        # Delete the record
        conn.execute(f"DELETE FROM {self.tablename} WHERE id = ?", (id,))
        conn.commit()
        return True
        
    def bulk_insert(self, items: list[Any]):
        """Insert many records into the table.
           More efficient than inserting one record at a time
        """
        if not self.model:
            raise ValueError("self.model must be defined when calling any database functions")
        if isinstance(items, self.model):
            items = [items]
        
        conn = self._get_conn()

        # Build the query template
        dump = items[0].model_dump()
        columns = ", ".join([k for k in dump.keys()])
        placeholders = ", ".join((["?"] * len(dump)))

        # Build query - SQLi safe (parameterized - see placeholders definition)
        query = f"INSERT INTO {self.tablename} ({columns}) VALUES ({placeholders})"

        # Collect values
        vals = []
        for datum in items:
            vals.append(list(datum.model_dump().values()))
        conn.executemany(query, vals)
        conn.commit()

    def get_by_column_value(self, column: str, value: Any) -> List[Any]:
        """Get patients by column value (for compatibility with CustomTable)"""
        if not self.model:
            raise ValueError("self.model must be defined when calling any database functions")
        
        conn = self._get_conn()
        cur = conn.execute(f"PRAGMA table_info({self.tablename})")
        cols = [r[1] for r in cur.fetchall()]

        if column not in cols:
            return []
        
        query = f"SELECT * FROM {self.tablename} WHERE {column} = ?"
        tmp = conn.execute(query, (value,)).fetchall()
        return [self.model(**dict(zip(self.model.model_fields, t))) for t in tmp]
    
    # TODO: Discuss limit on number of rows updated - makes data inconsistent
    def update_column(self, col_name: str, old_value: Any, new_value: Any, num_rows: int = -1) -> int:
        """Update column values (for compatibility with CustomTable). Return number of columns updated"""
        if not self.model:
            raise ValueError("self.model must be defined when calling any database functions")
        
        # Check if the column exists in the table
        conn = self._get_conn()
        cur = conn.execute(f"PRAGMA table_info({self.tablename})")
        cols = [r[1] for r in cur.fetchall()]

        if col_name not in cols:
            return []
        
        # Count updated rows
        query = f"SELECT COUNT(*) FROM {self.tablename} WHERE {col_name} = ?"
        updated_count = conn.execute(query, (old_value,)).fetchone()[0]

        # Update rows
        query = f"UPDATE {self.tablename} SET {col_name} = ? WHERE {col_name} = ?"
        conn.execute(query, (new_value, old_value))
        conn.commit()
        return updated_count
    
    def conditional_update_column(self, condition_col: str, condition_value: Any, 
                                update_col: str, new_value: Any) -> int:
        """Conditionally update column values (for compatibility with CustomTable)"""
        if not self.model:
            raise ValueError("self.model must be defined when calling any database functions")
        
        # Check if the column exists in the table
        conn = self._get_conn()
        cur = conn.execute(f"PRAGMA table_info({self.tablename})")
        cols = [r[1] for r in cur.fetchall()]

        if condition_col not in cols or update_col not in cols:
            return []
        
        # Count updated rows
        query = f"SELECT COUNT(*) FROM {self.tablename} WHERE {condition_col} = ?"
        updated_count = conn.execute(query, (condition_value,)).fetchone()[0]

        # Update rows
        query = f"UPDATE {self.tablename} SET {update_col} = ? WHERE {condition_col} = ?"
        conn.execute(query, (new_value, condition_value))
        conn.commit()
        return updated_count
