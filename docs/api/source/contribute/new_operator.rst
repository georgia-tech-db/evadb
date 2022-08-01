.. _guide-operators:

Adding New Operators/Commands
===================

    This section describes practices to follow when adding support for new operators/commands into EVA.

Parsing
--------
* Add word/query vocabulary to evaql_lexer.g4
* Add command structure to evaql_parser.g4
* Add type of Command to eva/parser/types.py
* Add Node structure to eva/parser/table_ref.py (If Applicable)
  * Changes to TableRef (If Applicable)
* Add Parser Code to eva/parser/parser_visitor depending on type
  * If table parser, then add code to eva/parser/parser_visitor/_table_sources.py

Optimizer (Statement to Logical Plan Converter)
--------
* Add Operator/LogicalPlans (Class) to eva/optimizer/operators.py
* Add Rules of optimization to eva/optimizer/rules/rules.py
* Add code to convert statement to LogicalPlans in eva/optimizer/statement_to_opr_convertor.py


Physical Plan (Logical to Physical Generator)
--------
* Add type of plan to eva/planner/types.py
* Add individual plans as python files in eva/planner/ using the type defined in previous type

Execution
--------
* Add individual executor files to eva/exector/
