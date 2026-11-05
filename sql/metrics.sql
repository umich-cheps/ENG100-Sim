--- Core SimuCore Table (Metrics)
CREATE SEQUENCE IF NOT EXISTS metrics_id_seq;

-- Metrics
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY DEFAULT nextval('metrics_id_seq'),
    replication_id INTEGER,
    percent_high_capacity_used FLOAT,
    percent_gen_capacity_used FLOAT,
    percent_gen_capacity_used_by_high FLOAT,
    percent_gen_capacity_used_by_low FLOAT,
    average_wait_time FLOAT,
    average_high_priority_wait_time FLOAT, 
    average_low_priority_wait_time FLOAT,
    max_overall_wait_time FLOAT,
    max_high_priority_wait_time FLOAT,
    max_low_priority_wait_time FLOAT
)
