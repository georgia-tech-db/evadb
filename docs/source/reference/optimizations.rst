.. _optimizations:

EvaDB Optimizations 🛠️
======================

EvaDB optimizes the evaluation of *AI functions* using these optimizations:

1️⃣ *Function Result Caching*: EvaDB caches results of expensive function invocations during query processing. This accelerates subsequent queries over the same dataset. 📂

2️⃣ *Query Predicate Reordering*: Efficiency is key. EvaDB strategically reorders query predicates to prioritize evaluation of lower-cost and more selective predicates. 🔀

3️⃣ *Parallel Query Processing*: EvaDB runs AI models in parallel to optimize GPU utilization by leveraging the Ray execution framework. Additionally, an AI pipeline is established for concurrent CPU tasks, such as data loading and decoding. 🎩

These built-in optimizations ensure superior performance and responsiveness in EvaDB's AI function evaluations. Dive in and experience the EvaDB difference! 🌟🎉

.. include:: ../shared/designs/design6.rst