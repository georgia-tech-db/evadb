# System Workflow
* `server` - System launches and emits client commands to command handler. 
* `parser` - System parses SQL and converts it to statement.
* It mainly generates CREATE, SELECT, INSERT, and LOAD, etc statements.
* For SELECT statement, some tokens are direclty mapped to expressions(`expression`). E.g., UDF is mapped to function expression. 
* `optimizer / statement_to_opr_convertor.py` - System converts a statement to an operator represented in tree structure(`optimizer / operators.py`). 
* For statements other than SELECT, it is mostly one - to - one mapping from statement to operator.
* For SELECT statement, it is expanded to different operators PROJECT and FILTER, etc.
* `optimizer / plan_generator.py` - System runs query optimization first.
* All operators in the tree are converted to group expression for optimization(`optimizer / group_expression.py`).
* Apply rewrite based on rules(`optimizer / rules`).
* `optimizer / plan_generator.py` - System builds physical plans(`planner`) based on the optimal logical plan.
* `executor` - System executes the physical plans. 
