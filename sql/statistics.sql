--- Core SimuCore Table (Statistics)
CREATE SEQUENCE IF NOT EXISTS statistics_id_seq;

-- Name in quotes for portability since "statistics" is a reserved
--  keyword in some SQL engines
CREATE TABLE IF NOT EXISTS "statistics" (
    id INTEGER PRIMARY KEY DEFAULT nextval('statistics_id_seq'),
    metric_name VARCHAR,
    mean FLOAT,
    median FLOAT,
    ci_low FLOAT,
    ci_high FLOAT
)
