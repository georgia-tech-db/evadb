.. _setup_pypi_account:

Setup PyPI Account
==================

Make sure you have `PyPI <https://pypi.org>`_ account with maintainer access to the EvaDB project. 
Create a .pypirc in your home directory. It should look like this:

.. code-block:: python

    [distutils]
    index-servers =
    pypi
    pypitest
    
    [pypi]
    username=YOUR_USERNAME
    password=YOUR_PASSWORD

Then run ``chmod 600 ~/.pypirc`` so that only you can read/write the file.
