Code Style
============

We use the `black <https://github.com/psf/black>`__ code style for
formatting the Python code. For docstrings and documentation, we use
`Google Pydoc format <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`__.

.. code-block:: python

   def function_with_types_in_docstring(param1, param2) -> bool:
       """Example function with types documented in the docstring.

       Additional explanatory text can be added in paragraphs.

       Args:
           param1 (int): The first parameter.
           param2 (str): The second parameter.

       Returns:
           bool: The return value. True for success, False otherwise.