.. LOAD PDF
.. ==========

.. .. _load-document:

.. .. code:: mysql

..    LOAD DOCUMENT 'test_doc.doctype' INTO MyDOCs;

.. Documents can be directly imported into a table using this function. How the document is added to the table varies depending upon the document type.

.. Supported document types are: ".csv", ".doc", ".docx", ".enex", ".eml", ".epub", ".html", ".md", ".pdf", ".ppt", ".pptx", ".txt"



LOAD PDF
=========

Load Document
-------------

.. _load-document:

Loads a document into a table.

```mysql
LOAD DOCUMENT 'test_doc.doctype' INTO MyDOCs;

Description:
Documents can be directly imported into a table using this function. The method of adding the document to the table varies depending on the document type.

Supported document types:

".csv"
".doc"
".docx"
".enex"
".eml"
".epub"
".html"
".md"
".pdf"
".ppt"
".pptx"
".txt"