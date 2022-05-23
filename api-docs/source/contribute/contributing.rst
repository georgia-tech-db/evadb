.. _guide-contributing:

Contributing
=============
To file a bug or request a feature, please file a GitHub issue. Pull requests are welcome.

See the `people page <https://github.com/georgia-tech-db/eva/graphs/contributors>`_ for the full listing of contributors.

Packaging New Version Of EVA
=============

1. Generate EVA grammar files.
```shell
bash script/antlr4/generate_parser.sh
```

2. Bump up version number in `setup.cfg` along with any additional dependencies.

3. Create a new build locally.
```shell
python -m build
```

4. Upload build to pypi using credentials.
```shell
python -m twine upload dist/*
```
