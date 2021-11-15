.. _guide-overview:

Overview
============

EVA brings structure the power of SQL to your video data.

- Build **super apps** over your video data by leveraging EVA’s simple SQL-like interface.
- Trying to find a tradeoff between throughput and accuracy on your video models? EVA can give you both:
    - EVA **improves throughput** by introducing sampling, filtering, and caching techniques.
    - EVA **improves accuracy** by introducing state-of-the-art model specialization and selection algorithms.
- EVA offers seamless integration into your existing model workflows with the power of EVA UDF’s. (Need to change wording from UDF to something else).


EVA consists of four core components:

- EVAQL Query Parser
- Query Optimizer
- Query Execution Engine (Filters + Deep Learning Models)
- Distributed Storage Engine
