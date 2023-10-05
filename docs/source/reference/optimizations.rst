.. _optimizations:

EvaDB Optimizations 🛠️
======================

EvaDB optimizes the evaluation of AI functions using these optimizations:

1️⃣ Result Caching: EvaDB caches outcomes from expensive function invocations during query processing. This approach facilitates faster retrieval in subsequent queries. 📂

2️⃣ Predicate Reordering: Efficiency is key. EvaDB strategically reorders predicates to prioritize lower-cost and more selective evaluations. ⚖️

3️⃣ Parallel Processing with Ray: Leveraging the Ray framework, EvaDB runs AI models in parallel, optimizing GPU utilization. Additionally, an AI pipeline is established for concurrent CPU tasks, such as data loading and decoding. 🚀

These techniques ensure superior performance and responsiveness in EvaDB's AI function evaluations.
