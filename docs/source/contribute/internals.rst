EVA Internals
=============

Path of a Query
-------------------

The following code represents a sequence of operations that can be used to execute a query in a evaql database. found in `eva/server/command_handler.py <https://github.com/georgia-tech-db/eva/blob/076704705c35245a6c83a626dba599342c59ff64/eva/server/command_handler.py#L37>`_

    Parse the query using the Parser() function provided by the evaql library. The result of this step will be a parsed representation of the query in the form of an abstract syntax tree (AST).

.. code:: python

    stmt = Parser().parse(query)[0]

Bind the parsed AST to a statement context using the StatementBinder() function. This step resolves references to schema objects and performs other semantic checks on the query.

.. code:: python

    StatementBinder(StatementBinderContext()).bind(stmt)

Convert the bound AST to a logical plan using the StatementToPlanConvertor() function. This step generates a logical plan that specifies the sequence of operations needed to execute the query.

.. code:: python

    l_plan = StatementToPlanConvertor().visit(stmt)

Generate a physical plan from the logical plan using the plan_generator.build() function. This step optimizes the logical plan and generates a physical plan that specifies how the query will be executed.

.. code:: python

    p_plan = plan_generator.build(l_plan)

Execute the physical plan using the PlanExecutor() function. This step retrieves the data from the database and produces the final output of the query.

.. code:: python

    output = PlanExecutor(p_plan).execute_plan()

Overall, this sequence of operations represents the path of query execution in a evaql database, from parsing the query to producing the final output.

Topics
------

.. tableofcontents::
