.. _guide-overview:

Overview
============

EVA is a visual data management system (think MySQL for videos). It supports a declarative language similar to SQL and a wide range of commonly used  computer vision models.

- EVA **enables querying of visual data** in user facing applications by providing a simple SQL-like interface for a wide range of commonly used computer vision models.
- EVA **improves throughput** by introducing sampling, filtering, and caching techniques.
- EVA **improves accuracy** by introducing state-of-the-art model specialization and selection algorithms.

EVA consists of four core components:
- EVAQL Query Parser
- Query Optimizer
- Query Execution Engine (Filters + Deep Learning Models)
- Distributed Storage Engine
