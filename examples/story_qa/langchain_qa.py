import faiss
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.llms import GPT4All
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

from examples.story_qa.util import download_story


def download_model(local_path):
    import requests

    from pathlib import Path
    from tqdm import tqdm

    Path(local_path).parent.mkdir(parents=True, exist_ok=True)

    # skip downloading the model
    if Path(local_path).exists():
        return
    # Example model. Check https://github.com/nomic-ai/gpt4all for the latest models.
    url = "http://gpt4all.io/models/ggml-gpt4all-j-v1.3-groovy.bin"

    # send a GET request to the URL to download the file. Stream since it's large
    response = requests.get(url, stream=True)

    # open the file in binary mode and write the contents of the response to it in chunks
    # This is a large file, so be prepared to wait.
    with open(local_path, "wb") as f:
        for chunk in tqdm(response.iter_content(chunk_size=8192)):
            if chunk:
                f.write(chunk)


model_path = "./ggml-gpt4all-j-v1.3-groovy"
download_model(model_path)

# Download The Project Gutenberg eBook of War and Peace
book_path = download_story()

# setup the model
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
llm = GPT4All(
    model=model_path,
    backend="gptj",
    callbacks=callback_manager,
    verbose=False,
    n_threads=16,
)

# setup the hugging face embeddding model
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {"device": "gpu"}
hf_embeddings = HuggingFaceEmbeddings(
    model_name=embedding_model_name,
    model_kwargs=model_kwargs,
)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_text(open(book_path).read())

# create FAISS vector index based on HuggingFace Embeddings
store = FAISS.from_texts(
    texts,
    hf_embeddings,
    metadatas=[
        {"source": f"Text chunk {i} of {len(texts)}"} for i in range(len(texts))
    ],
)
# creating QA model based on gpt4all llm model
qa = RetrievalQA.from_chain_type(
    llm=llm, chain_type="stuff", retriever=store.as_retriever()
)

for question in open("questions.txt").readline():
    # fetching answer based question
    ans = qa.run(question)
    print("Question: {question} \n Answer {ans}")
