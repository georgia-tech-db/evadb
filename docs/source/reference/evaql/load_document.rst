LOAD PDF
==========

.. _load-document:

.. code:: mysql

   LOAD DOCUMENT 'test_doc.doctype' INTO MyDOCs;

Documents can be directly imported into a table using this function. How the document is added to the table varies depending upon the document type.

Supported document types are:
| ``".csv",
    ".doc",
    ".docx",
    ".enex",
    ".eml",
    ".epub",
    ".html",
    ".md",
    ".pdf",
    ".ppt",
    ".pptx",
    ".txt"``
