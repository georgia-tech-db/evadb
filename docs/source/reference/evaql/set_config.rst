SET CONFIGS
==============

.. _set_config:

Sets the value of a configuration parameter to the passed value. Both `TO` and `=` are valid assignment operators.

.. code:: sql

    SET OPENAI_KEY TO "abc";
    SET OPENAI_KEY = "abc";

.. note::

    The `SET` command does not support `CONFIG` or `CONFIGS` as keys names. This is because `CONFIG` and `CONFIGS` are reserved keywords.
