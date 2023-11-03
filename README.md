## Integration of Alembic with EvaDB
Alembic is a Python database migration tool for relational databases. With SQLAlchemy as its foundation, Alembic works with the “change management scripts” to manage table schemas through upgrade and downgrade functions while tracking revisions.

Currently whenever we modify a table in EvaDB (e.g., add a column to a catalogue table), the folder evadb-data gets deleted. To reduce this overhead, Alembic could be introduced into EvaDB and facilitate database migration more easily.

## License
Copyright (c) [Georgia Tech Database Group](http://db.cc.gatech.edu/).
Licensed under an [Apache License](LICENSE.txt).
