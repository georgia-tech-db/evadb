## Installation 

Recommendation: When installing Java and MySQL, allow updates to your PATH variable. This will allow the given programs to run from your main CMD.

Installation of EVA involves setting a virtual environment using [miniconda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) and configuring git hooks.

After installing Anaconda and activating the 'eva' virtual environment:
 1. If your windows machine does not allow you to run shell scripts, navigate to eva/script, and execute the commands in each script manually. 

2. generate_parser.sh requires Java, which can be downloaded at https://www.java.com/en/download/.

3. Installation of EVA also involves downloading the MySQL database via https://dev.mysql.com/downloads/. The tables from EVA are stored in a MySQL database.

4. Create a database called 'eva_catalog' in either MySQL workbench or through the MySQL command line client. The username and password for 'eva_catalog' should be blank. 

5. Run the following command from the 'eva' directory to ensure everything is working:
```shell
python -m pytest test\parser\test_parser.py
```