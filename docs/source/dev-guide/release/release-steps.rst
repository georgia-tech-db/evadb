.. _release_steps:


Release Steps
=============

Update Version 
~~~~~~~~~~~~~~~

Update the new version number in ``evadb/version.py``.


Update ``master`` with ``staging``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simply point ``master`` head to the latest commit of ``staging``.

.. code-block:: bash

    git checkout master
    git reset --hard <latest commit of staging>
    git push -f origin master


Setup Credentials
~~~~~~~~~~~~~~~~~~

Please check :ref:`setup_pypi_account` about how to setup PyPi account.

Setup Github token. You can obtain a personal token from Github.

.. code-block:: bash

    export GITHUB_KEY="..."

Build Wheel and Release
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python script/releasing/releaser.py -n minor -u
