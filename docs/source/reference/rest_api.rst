.. _rest_api:

REST API Usage 
======================
To start the EvaDB server, run the following command:

.. code-block:: python

    cd evadb/apps/rest
    python run_evadb.py

Now that the server is setup, we can access EvaDB through REST APIs using two endpoints shown below:

Query API

Here's an example to run a QUERY locally using the API in python.

.. code-block:: python

    import requests
    query_url = "http://127.0.0.1:5000/query"
    response = requests.post(query_url, {'query':'Select * from data;'})
    print(response.json())

Upload API

1️⃣ Users can upload any files of type {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3'} to the EVA DB server.
Here's an example to upload a local file using the API in python.

.. code-block:: python
    
    import requests
    query_url = "http://127.0.0.1:5000/upload"
    myfiles = {'file': open('<path to file>' ,'rb')}
    response = requests.post(load_url, files = myfiles)
    print(response.json())

2️⃣ Users can also paste the above url in the browser, and the user can upload the document through "upload" button.

3️⃣ The files are stored in the file section which can then be accessed through the query API using the LOAD query.

