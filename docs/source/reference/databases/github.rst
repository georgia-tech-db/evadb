Github
==========

The connection to Github is based on the `PyGithub <https://github.com/PyGithub/PyGithub>`_ library.

Dependency
----------

* PyGithub


Parameters
----------

Required:

* ``owner`` is the owner of the Github repository. For example, georgia-tech-db is the owner of the EvaDB repository.
* ``repo`` is the name of the Github repository. For example, evadb is the name of this repository.

Optional:

* ``github_token`` is not required for public repositories. However, the rate limit is lower without a valid github_token. Check `Rate limits page <https://docs.github.com/en/rest/overview/resources-in-the-rest-api?apiVersion=2022-11-28#rate-limits>`_ to learn more about how to check your rate limit status. Check `Managing your personal access tokens page <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens>`_ to learn how to create personal access tokens.

Create Connection
-----------------

.. code-block:: text

   CREATE DATABASE github_data WITH ENGINE = 'github', PARAMETERS = {
        "owner": "georgia-tech-db",
        "repo": "evadb"
   };

Supported Tables
----------------

* ``stargazers``: Lists the people that have starred the repository. Check `evadb/third_party/databases/github/table_column_info.py` for all the available columns in the table.

.. code-block:: sql

   SELECT * FROM github_data.stargazers;

Here is the query output:

.. code-block:: 

    +---------------------------------------------------+-----+---------------------------------------------+
    |                             stargazers.avatar_url | ... |                              stargazers.url |
    |---------------------------------------------------|-----|---------------------------------------------|
    | https://avatars.githubusercontent.com/u/105357... | ... |      https://api.github.com/users/jaehobang |
    | https://avatars.githubusercontent.com/u/436141... | ... | https://api.github.com/users/VineethAljapur |
    +---------------------------------------------------+-----+---------------------------------------------+

.. note::

   Looking for another table from Github? You can add a table mapping in `evadb/third_party/databases/github/github_handler.py`, or simply raise a `Feature Request <https://github.com/georgia-tech-db/evadb/issues/new/choose>`_.
