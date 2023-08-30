:orphan:

===
FAQ
===

These are some Frequently Asked Questions that we've seen pop up for EvaDB.

If you still have questions after reading this FAQ,  ping us on
`our Slack <https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg>`__!

Why am I not able to install EvaDB in my Python environment?
============================================================

Ensure that the local Python version is >= 3.8 and <= 3.10. EvaDB cannot support 3.11 due to its `dependency on Ray <https://github.com/autogluon/autogluon/issues/2687>`__.

Where does EvaDB store all the data?
====================================

By default, EvaDB stores all the data in a local folder named ``evadb_data``. Deleting this folder will reset the system's state and lead to data loss.

Why does the EvaDB server not start?
====================================

Check if another process is already running on the target port where EvaDB server is being launched (default port of EvaDB is ``8803``) using these commands:

.. code-block:: bash

    sudo lsof -i :<port_number>
    kill -9 <process_id>

You can either kill that process or launch EvaDB server on another free port in this way:

.. code-block:: bash

    evadb_server -p 9330

Why do I see no output from the server?
=======================================

If a query runs a complex vision task (such as object detection) on a long video, the query is expected to take a non-trivial amount of time to finish.
You can check the status of the server by running ``top`` or ``pgrep``:

.. code-block:: bash

    top
    pgrep evadb_server

pip install ray fails because of grpcio
=======================================

Follow these instructions to install ``ray``:
https://github.com/ray-project/ray/issues/33039
