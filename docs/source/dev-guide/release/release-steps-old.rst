:orphan:


Release Steps
=============

1. Ensure that you're in the top-level ``eva`` directory.
2. Ensure that your branch is in sync with the ``master`` branch:

.. code-block:: bash

       $ git pull origin master

3. Add a new entry in the Changelog for the release.

.. code-block:: python

       ##  [0.0.6]
       ### [Breaking Changes]
       ### [Added]
       ### [Changed]
       ### [Deprecated]
       ### [Removed]

Make sure ``CHANGELOG.md`` is up to date for the release: compare against PRs
merged since the last release.

4. Update version to, e.g. ``0.0.6`` (remove the ``+dev`` label) in ``evadb/version.py``.

5. Commit these changes and create a PR:

.. code-block:: bash

       git checkout -b release-v0.0.6
       git add . -u
       git commit -m "[RELEASE]: v0.0.6"
       git push --set-upstream origin release-v0.0.6

6. Once the PR is approved, merge it and pull master locally.

7. Tag the release:

.. code-block:: bash

       git tag -a v0.0.6 -m "v0.0.6 release"
       git push origin v0.0.6

8. Build the source and wheel distributions:

.. code-block:: bash

       rm -rf dist build  # clean old builds & distributions
       python3 setup.py sdist  # create a source distribution
       python3 setup.py bdist_wheel  # create a universal wheel

9. Check that everything looks correct by installing the wheel locally and checking the version:

.. code-block:: python

       python3 -m venv test_evadb  # create a virtualenv for testing
       source test_evadb/bin/activate  # activate virtualenv
       python3 -m pip install dist/evadb-0.9.1-py3-none-any.whl
       python3 -c "import evadb; print(evadb.__version__)"

10. Publish to PyPI

.. code-block:: python

       pip install twine  # if not installed
       twine upload dist/* -r pypi

11. A PR is automatically submitted (this will take a few hours) on [`conda-forge/eva-feedstock`] to update the version.
    * A maintainer needs to accept and merge those changes.

12. Create a new release on Github.
    * Input the recently-created Tag Version: ``v0.0.6``
    * Copy the release notes in ``CHANGELOG.md`` to the GitHub tag.
    * Attach the resulting binaries in (``dist/evadb-x.x.x.*``) to the release.
    * Publish the release.

13. Update version to, e.g. ``0.9.1+dev`` in ``evadb/version.py``.

14. Add a new changelog entry for the unreleased version in `CHANGELOG.md`:

.. code-block:: python

       ##  [Unreleased]
       ### [Breaking Changes]
       ### [Added]
       ### [Changed]
       ### [Deprecated]
       ### [Removed]

15. Commit these changes and create a PR:

.. code-block:: bash

       git checkout -b bump-v0.9.1+dev
       git add . -u
       git commit -m "[BUMP]: v0.9.1+dev"
       git push --set-upstream origin bump-v0.9.1+dev
       
16. Add the new tag to `the EvaDB project on ReadTheDocs <https://readthedocs.org/projects/evadb>`_,

    * Trigger a build for main to pull new tags.
    * Go to the ``Versions`` tab, and ``Activate`` the new tag.
    * Go to Admin/Advanced to set this tag as the new default version.
    * In ``Overview``, make sure a build is triggered:
        * For the tag ``v0.9.1``
        * For ``latest``

Credits: `Snorkel <https://github.com/snorkel-team/snorkel/blob/main/RELEASING.md>`_
