# Test for combining frontend (VQL) and backend(Eva) query optimizer

## Generate inputs for query optimizer
Transform the sql statement in test.txt to a list of parsed predicates and a list of opertors  
```
python3 temp.txt test.txt
```

## Furture work
Call query optimizer in test.txt with the generated lists;  
Deal with expressions on both sides of the logicalOperator are in parentheses. 