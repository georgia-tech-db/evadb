## EVA Read-the-Docs Documentation
Run the following commands from this directory to compile the documentation.

```
cd eva/docs
pip install -r requirements.txt
make html
open _build/html/index.html
```

To test links:

```
cd eva/docs
sphinx-build . _build -b linkcheck
```