# Story Question and Answering
This example demonstrates the capability of EvaDB in extracting embedding from texts, building similarity index, searching similar sources, and using LLM to answer question based on that. For this example, we use "War and Peace" story as the source for our demonstration purpose.

## Hardware Setup
For all examples in this folder, the performance results on measured on a server with AMD EPYC 7452 32-Cores CPU with `256`GB memory and one A40 NVIDIA GPU, which has `48`GB GPU memory.

## Single Question Answering
The major performance benefit of EvaDB in single question answering comes from its capability of parallelizing the feature extraction step.

### How to Run
```bash
python evadb_qa.py
```

### Performance Results
We set the degree of parallelism to `8` to compare with no parallelism. We also need to update the `batch_mem_size` to a small value (e.g., `1`) to encourage more data-level parallelism. The reason we obrain better performance is because we achieve better GPU utilization by overlapping the feature extractor computation better through parallelization.

|  | Feature Extraction Time | Total QA Time |
| --- | ----------------------- | ------------- |
| DOP=1 | 216846.221 ms | 299966.315 ms |
| DOP=8 | 101594.066 ms | 168546.058 |
| Speedup | 2.1 | 1.8 | 
