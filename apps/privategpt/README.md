# privateGPT

## Environment Setup
To set up your environment, install all the required dependencies by running the following command:

    ```shell
    pip3 install -r requirements.txt
    ```

## Try the App
Ingest the pds by executing the following command:

```shell
python ingest.py
```

This command will load the PDF files located in the `source_document` folder into the EvaDB  and build an index on it.


To ask questions to your documents locally, use the following command:

```shell
python privateGPT.py
```

Once you run this command, the script will prompt you for input.
```plaintext
> Enter your question: Why was NATO created?

> Answer:
The purpose of NATO was to secure peace and stability in Europe after World War 2. To accomplish this, American ground forces, air squadrons, and ship deployments were mobilized to protect NATO countries, including Poland, Romania, Latvia, Lithuania, and Estonia. Additionally, a coalition of other freedom-loving nations from Europe, Asia, and Africa was formed to confront Putin.
```

To exit the script, simply type `exit`.

Feel free to reach out if you have any questions or need further assistance.