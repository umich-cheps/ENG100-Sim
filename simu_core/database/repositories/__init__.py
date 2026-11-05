# Repository pattern package for data access
import duckdb

_ANCHOR = duckdb.connect(":memory:shared")