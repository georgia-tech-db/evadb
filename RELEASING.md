# EVA Release Guide

## Before You Start

Make sure you have [PyPI](https://pypi.org) account with maintainer access to the EVA project. 
Create a .pypirc in your home directory.
It should look like this:

```
[distutils]
index-servers =
  pypi
  pypitest

[pypi]
username=YOUR_USERNAME
password=YOUR_PASSWORD
```

Then run `chmod 600 ./.pypirc` so only you can read/write.

## Release Steps

1. Make sure you're in the top-level `eva` directory.
1. Make certain your branch is in sync with head:
   
       $ git pull origin master

1. Add a new changelog entry for the release.

       ##  [0.0.6]
       ### [Breaking Changes]
       ### [Added]
       ### [Changed]
       ### [Deprecated]
       ### [Removed]

  Make sure `CHANGELOG.md` is up to date for the release: compare against PRs
  merged since the last release.

1. Update version to, e.g. 0.0.6 (remove the `+dev` label) in `eva/version.py`.

1. Commit these changes and create a PR:

       git checkout -b release-v0.0.6
       git add . -u
       git commit -m "[RELEASE]: v0.0.6"
       git push --set-upstream origin release-v0.0.6

1. Once the PR is approved, merge it and pull master locally.

1. Tag the release:

       git tag -a v0.0.6 -m "v0.0.6 release"
       git push origin v0.0.6

1. Build source & wheel distributions:

       rm -rf dist build  # clean old builds & distributions
       python3 setup.py sdist  # create a source distribution
       python3 setup.py bdist_wheel  # create a universal wheel

1. Check that everything looks correct by installing the wheel locally and checking the version:

       python3 -m venv test_evadb  # create a virtualenv for testing
       source test_evadb/bin/activate  # activate virtualenv
       python3 -m pip install dist/evadb-0.9.1-py3-none-any.whl
       python3 -c "import eva; print(eva.__version__)"

1. Publish to PyPI

       pip install twine  # if not installed
       twine upload dist/* -r pypi

1. A PR is auto-submitted (this will take a few hours) on [`conda-forge/eva-feedstock`](https://github.com/conda-forge/eva-feedstock) to update the version.
    * A maintainer needs to accept and merge those changes.

1. Create a new release on Github.
    * Input the recently-created Tag Version: `v0.0.6`
    * Copy the release notes in `CHANGELOG.md` to the GitHub tag.
    * Attach the resulting binaries in (`dist/evadb-x.x.x.*`) to the release.
    * Publish the release.


1. Update version to, e.g. 0.9.1+dev in `eva/version.py`.

1. Add a new changelog entry for the unreleased version in `CHANGELOG.md`:

       ##  [Unreleased]
       ### [Breaking Changes]
       ### [Added]
       ### [Changed]
       ### [Deprecated]
       ### [Removed]

1. Commit these changes and create a PR:

       git checkout -b bump-v0.9.1+dev
       git add . -u
       git commit -m "[BUMP]: v0.9.1+dev"
       git push --set-upstream origin bump-v0.9.1+dev

       
1. Add the new tag to [the EVA project on ReadTheDocs](https://readthedocs.org/projects/evadb),
    * Trigger a build for main to pull new tags.
    * Go to the "Versions" tab, and "Activate" the new tag.
    * Go to Admin/Advanced to set this tag as the new default version.
    * In "Overview", make sure a build is triggered:
        * For the tag `v0.9.1`
        * For `latest`


## Credits
* [Snorkel](https://github.com/snorkel-team/snorkel/blob/main/RELEASING.md)
