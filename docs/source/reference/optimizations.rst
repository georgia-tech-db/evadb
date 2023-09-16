.. _optimizations:

Optimizations
=============

EvaDB optimizes the evaluation of user-defined functions in three manifolds.

1. Cache expensive function invocations and reuse their results in future invocations.
2. Cost-based predicate reordering to evaluate fast and selective predicate first.
3. Ray-based distributed inference. EvaDB not only parallelizes model inference to improve GPU utilization but also builds pipeline to parallelize CPU processing (i.e., loading and decoding data).
