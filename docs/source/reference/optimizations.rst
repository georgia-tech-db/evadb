.. _optimizations:

Optimizations
=============

EvaDB optimizes the evaluation of AI functions using these optimizations:

1. EvaDB automatically caches the results of expensive function invocations while processing a query and reuses the results in future queries.
2. EvaDB reorder predicates based on cost to evaluate fast, more selective predicates earlier.
3. EvaDB runs AI models using the Ray framework in parallel to improve GPU utilization and sets up an AI pipeline to parallelize CPU processing (i.e., loading and decoding data).


