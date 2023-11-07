LOAD PDF
==========

.. _load-pdf:

.. code:: mysql

   LOAD PDF 'test_pdf.pdf' INTO MyPDFs;

The PDF document is segmented into pages and then paragraphs and the paragraphs are loaded into a table.

Each row in the table corresponds to a paragraph extracted from the PDF, and the resulting table includes columns for ``name`` , ``page``, ``paragraph``, and ``data``.

- ``name`` signifies the name of the uploaded PDF.
- ``page`` signifies the specific page number from which the data is retrieved.
- ``paragraph`` signifies the individual paragraph number within a page from which the data is extracted.
- ``data``  refers to the text extracted from that paragraph.