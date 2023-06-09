# PrivateGPT in SQL with EvaDB

This project was inspired by the original [privateGPT](https://github.com/imartinez/privateGPT) and [localGPT](https://github.com/PromtEngineer/localGPT) projects.Most of the description is derived from these projects.

In this project, we use EvaDB to replicate the privateGPT workflow using SQL-like queries. We plan to add these two features in the coming week:

1. Improving the quality of answers by building hierarchical index over the documents at different granularities (sentences, paragraphs, and entire documents).
2. Besides text documents, EvaDB also supports search over images and videos.

You can ask questions on your documents without an internet connection using the power of LLMs. 100% private, no data leaves your execution environment at any point.

Built with [EvaDB](https://github.com/georgia-tech-db/eva), [LangChain](https://github.com/hwchase17/langchain), and [GPT4ALL](https://github.com/nomic-ai/gpt4all).

# Environment Setup
To use this software, you must have Python 3.8 or later installed. 

To set up your environment, install all the required dependencies by running the following command:

```shell
pip install -r requirements.txt
```

## Ask questions to your documents, locally!

Ingest the pdfs by executing the following command:

```shell
python ingest.py
```

This command will load the PDF files located in the `source_documents` folder into the EvaDB and build an index on it.

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

If you face any issues, please create an issue on [Github](https://github.com/georgia-tech-db/eva) or ping us on [Slack](https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg).


## Instructions for ingesting your own dataset

Put any and all of your .txt, .pdf, or .csv files into the `source_documents` directory. The current default file types are .txt, .pdf, .csv, and .xlsx, if you want to use any other file type, you will need to convert it to one of the default file types.
