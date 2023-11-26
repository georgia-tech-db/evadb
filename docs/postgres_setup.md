## INSTRUCTIONS TO SET UP POSTGRES DATABASE

These were the steps followed on a Mac system to install postgres and configure it:

1. Install postgres
   ``` brew install postgresql```
2. Start PostgresSQL:
```brew services start postgressql```
3. Create a user and database: 
   
   Username: evadb

   Password: password

   - ```psql postgres``` 
   - ```CREATE ROLE evadb WITH LOGIN PASSWORD 'password';```
   - ```ALTER ROLE evadb CREATEDB;```
   - ```\q```
4. Login as your new user

    ``` psql -d postgres -U evadb```
5. create the database evadb

    ```CREATE DATABASE evadb;```
6. ```pip install psycopg2```