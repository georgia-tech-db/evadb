Extending EVA 
=============

This document details the steps involved in adding support for a new operator (or command) in EVA. We illustrate the process using a DDL command.

Command Handler
----

An input query string is handled by **Parser**,
**StatementTOPlanConverter**, **PlanGenerator**, and **PlanExecutor**. 
We discuss each part separately.

.. code:: python

   def execute_query(query) -> Iterator[Batch]:
       """
       Execute the query and return a result generator.
       """
       #1. parser
       stmt = Parser().parse(query)[0]
       #2. statement to logical plan
       l_plan = StatementToPlanConverter().visit(stmt)
       #3. logical to physical plan
       p_plan = PlanGenerator().build(l_plan)
       #4. parser
       return PlanExecutor(p_plan).execute_plan()

.. _1-parser:

1. Parser
---------

The parser firstly generate **syntax tree** from the input string, and
then transform syntax tree into **statement**.

The first part of Parser is build from a LARK grammar file.

parser/eva
~~~~~~~~~~~~

-  ``eva.lark`` - add keywords(eg. CREATE, TABLE) under **Common
   Keywords**

   -  Add new grammar rule (eg. create_table)
   -  Write a new grammar, for example:

   ::

      create_table: CREATE TABLE if_not_exists? table_name create_definitions 


--------------

The second part of parser is implemented as **parser visitor**.

parser/lark_visitor
~~~~~~~~~~~~~~~~~~~~~

-  ``_[cmd]_statement.py`` - eg. class CreateTable(evaql_parserVisitor)

   -  Write functions to transform each input data from syntax tree to
      desired type. (eg. transform Column information into a list of
      ColumnDefinition)
   -  Write a function to construct [cmd]Statement and return it.

-  ``__init__.py`` - import ``_[cmd]_statement.py`` and add its class to
   ``ParserVisitor``'s parent class.

.. code:: python

   from src.parser.parser_visitor._create_statement import CreateTable
   class ParserVisitor(CommonClauses, CreateTable, Expressions,
                       Functions, Insert, Select, TableSources,
                       Load, Upload):

parser/
~~~~~~~

-  ``[cmd]_statement.py`` - class [cmd]Statement. Its constructor is
   called in ``_[cmd]_statement.py``
-  ``types.py`` - register new StatementType

.. _2-statementtoplanconverter:

2. Statement To Plan Converter
---------------------------

The part transforms the statement into corresponding logical plan.

Optimizer
~~~~~~~~~

-  ``operators.py``

   -  Define class Logical[cmd], which is the logical node for the
      specific type of command.

   .. code:: python

      class LogicalCreate(Operator):
          def __init__(self, video: TableRef, column_list: List[DataFrameColumn], if_not_exists: bool = False, children=None):
          super().__init__(OperatorType.LOGICALCREATE, children)
          self._video = video
          self._column_list = column_list
          self._if_not_exists = if_not_exists
          # ...

   -  Register new operator type to **class OperatorType**, Notice that
      must add it **before LOGICALDELIMITER** !!!

-  ``statement_to_opr_convertor.py``

   -  import resource

   .. code:: python

      from src.optimizer.operators import LogicalCreate
      from src.parser.rename_statement import CreateTableStatement

   -  implement **visit_[cmd]()** function, which converts statement to
      operator

   .. code:: python

      # May need to convert the statement into another data type.
      # The new data type is usable for executing command.
      # For example, column_list -> column_metadata_list

      def visit_create(self, statement: AbstractStatement):
          video_ref = statement.table_ref
          if video_ref is None:
              LoggingManager().log("Missing Table Name In Create Statement",
                                   LoggingLevel.ERROR)

          if_not_exists = statement.if_not_exists
          column_metadata_list = create_column_metadata(statement.column_list)

          create_opr = LogicalCreate(
              video_ref, column_metadata_list, if_not_exists)
          self._plan = create_opr

   -  modify visit function to call the right visit_[cmd] function

   .. code:: python

      def visit(self, statement: AbstractStatement):
          if isinstance(statement, SelectStatement):
              self.visit_select(statement)
          #...
          elif isinstance(statement, CreateTableStatement):
              self.visit_create(statement)
          return self._plan

.. _3-plangenerator:

3. Plan Generator
----------------

The part transformed logical plan to physical plan. The modified files
are stored under **Optimizer** and **Planner** folders.

plan_nodes/
~~~~~~~~

-  ``[cmd]_plan.py`` - class [cmd]Plan, which stored information
   required for rename table.

.. code:: python

   class CreatePlan(AbstractPlan):
       def __init__(self, video_ref: TableRef,
                    column_list: List[DataFrameColumn],
                    if_not_exists: bool = False):
           super().__init__(PlanOprType.CREATE)
           self._video_ref = video_ref
           self._column_list = column_list
           self._if_not_exists = if_not_exists
       #...

-  ``types.py`` - register new plan operator type to PlanOprType

optimizer/rules
~~~~~~~~~~~~~~~

-  ``rules.py``-

   -  Import operators
   -  Register new ruletype to **RuleType** and **Promise** (place it
      **before IMPLEMENTATION_DELIMITER** !!)
   -  implement class ``Logical[cmd]ToPhysical``, its member function
      apply() will construct a corresponding\ ``[cmd]Plan`` object.

   .. code:: python

      class LogicalCreateToPhysical(Rule):
          def __init__(self):
          pattern = Pattern(OperatorType.LOGICALCREATE)
          super().__init__(RuleType.LOGICAL_CREATE_TO_PHYSICAL, pattern)

      def promise(self):
          return Promise.LOGICAL_CREATE_TO_PHYSICAL

      def check(self, before: Operator, context: OptimizerContext):
          return True

      def apply(self, before: LogicalCreate, context: OptimizerContext):
          after = CreatePlan(before.video, before.column_list, before.if_not_exists)
          return after

-  ``rules_base.py``-

   -  Register new ruletype to **RuleType** and **Promise** (place it
      **before IMPLEMENTATION_DELIMITER** !!)

-  ``rules_manager.py``-

   -  Import rules created in ``rules.py``
   -  Add imported logical to physical rules to ``self._implementation_rules``

.. _4-PlanExecutor:

4. Plan Executor
--------------

``PlanExecutor`` uses data stored in physical plan to run the command.

executor/
~~~~~~~~~

-  ``[cmd]_executor.py`` - implement an executor that make changes in
   **catalog**, **metadata**, or **storage engine** to run the command.

   -  May need to create helper function in CatalogManager,
      DatasetService, DataFrameMetadata, etc.

   .. code:: python

      class CreateExecutor(AbstractExecutor):
          def exec(self):
              if (self.node.if_not_exists):
                  # check catalog if we already have this table
                  return

              table_name = self.node.video_ref.table_info.table_name
              file_url = str(generate_file_path(table_name))
              metadata = CatalogManager().create_metadata(table_name, file_url, self.node.column_list)

              StorageEngine.create(table=metadata)

Additional Notes
--------------------

Key data structures in EVA:

-  **Catalog**: Records ``DataFrameMetadata`` for all tables.

   -  data stored in DataFrameMetadata: ``name``, ``file_url``, ``identifier_id``,
      ``schema``

      -  ``file_url`` - used to access the real table in storage engine.

   -  For the ``RENAME`` table command, we use the ``old_table_name`` to access the corresponding entry in metadata table, and the ``modified name`` of the table.

-  **Storage Engine**:

   -  API is defined in ``src/storage``, currently only supports
      create, read, write.
