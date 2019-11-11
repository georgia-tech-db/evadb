CREATE TABLE IF NOT EXISTS pp_filter(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    reduction_rate REAL NOT NULL,
    filter_cost REAL NOT NULL,
    accuracy REAL NOT NULL,
    udf_cost REAL NOT NULL,
    dataset_name TEXT NOT NULL,
    model_type TEXT DEFAULT NULL
);