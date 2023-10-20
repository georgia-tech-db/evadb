We can now access evadb through REST apis. The two API's used are as follows:

1) Query API
    * Through this API, the user can access EVADB by passing the query to the given request
        Eg: http://127.0.0.1:5000/query is the API to access the API. The user can then enter the API as required. 

2) Upload API
    * Users can upload any files of type {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3'} to the EVA DB server
    * This can be done through a post request containing a file in the request section
    * The API also allows the user to upload the document through "upload" button. 
    * The files are stored in the file section which can then be accessed through the query API with the "load" query.

    