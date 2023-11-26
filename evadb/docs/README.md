## EvaDB Read-the-Docs Documentation
Run the following commands from this directory to compile the documentation.

```
cd evadb/docs
pip install -r requirements.txt
make html
open _build/html/index.html
```

To further test external links:

```
make linkcheck
```
