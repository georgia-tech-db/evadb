## Integration of Alembic with EvaDB
Alembic works with the “change management scripts” to manage table schemas through `upgrade` and `downgrade` functions while tracking revisions. Therefore, it could be helpful in migrating the seven metadata table schemas whenever a newer version of EvaDB is released with changes to them.

## DEMO
### Migration Scripts
In `alembic/versions` two example migration scripts can be found:
- `b0ecb091fa7b_edit_a_column_in_table_catalog.py`
- `e6dc73b305fe_first_migration_adding_a_new_column_to_.py`

These scripts are created using the command `alembic revision -m <description for this revision>`. In the scripts we define two functions `upgrade` to make desired changes to tables or databases, and `downgrade` to revert the changes. The followins are some of the common commands for managing revisions:

- Display the current revision for a database: `alembic current`
- View migrations history: `alembic history --verbose`
- Revert all migrations: `alembic downgrade base`
- Apply all migrations: `alembic upgrade head`
- Apply specified revisionL `alembic upgrade <revision ID>`
- Reset the database: `alembic downgrade base && alembic upgrade head`

### Automigration Scripts
In the scenario where we would like to update the catalog tables along with the new release of EvaDB, the migration is expected to be done automatically. Therefore, `alembic_automigration.py` is provided to detect any newer revision and update accordingly. This script can be triggered either in `setup.py` or other release management tools.

## License
Copyright (c) [Georgia Tech Database Group](http://db.cc.gatech.edu/).
Licensed under an [Apache License](LICENSE.txt).
