# Experimental 

Experimental techniques that can be enabled optionally in the EVA system.

## Parallel Execution

Experimental approach to enable operator-level parallelization. During parallelization, the targeted operator becomes the inner operator of Exchange operator, which is in charge of parallelizing its associated inner operator.

We provide an example here to demonstrate how parallelization is done. 

![parallel-design-plot](./../../assets/parallel-design.jpg)