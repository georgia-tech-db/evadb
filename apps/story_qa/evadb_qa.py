from gpt4all import GPT4All
from unidecode import unidecode
from util import download_story, read_text_line
import evadb


def ask_question(path):
    # Initialize early to exlcude download time.
    llm = GPT4All("ggml-gpt4all-j-v1.3-groovy")
    llm.model.set_thread_count(16)

    cursor = evadb.connect().cursor()

    story_table = "story_table"
    story_feat_table = "feature_table"
    index_table = "index_table"

    print("Setup UDF")

    Text_feat_udf_query = """CREATE UDF IF NOT EXISTS           SentenceTransformerFeatureExtractor
            IMPL  'evadb/udfs/sentence_transformer_feature_extractor.py';
            """

    cursor.query(Text_feat_udf_query).execute()

    cursor.drop_table(story_feat_table).execute()
    cursor.drop_index(index_table).execute()
    cursor.drop_table(story_table).execute()

    cursor.query("CREATE TABLE story_table (id INTEGER, data TEXT(1000));").execute()

    # Insert text chunk by chunk.
    print("Creating table using the provided text")
    for i, text in enumerate(read_text_line(path)):
        ascii_text = unidecode(text)
        cursor.query(
            f"INSERT INTO story_table (id, data) VALUES ({i}, '{ascii_text}');"
        ).execute()

    # Extract features from text.
    print("Extracting Features")
    cursor.query(
        f"""CREATE TABLE story_feat_table AS
        SELECT SentenceTransformerFeatureExtractor(data), data FROM {story_table};"""
    ).execute()

    # Create search index on extracted features.
    cursor.create_vector_index(
        index_name="index_table",
        table_name="story_feat_table",
        expr="features",
        using="FAISS",
    )

    question = "Who is Cyril Vladmirovich?"

    ascii_question = unidecode(question)

    context_docs = (
        cursor.table("story_table")
        .order(
            f"""Similarity(SentenceTransformerFeatureExtractor('{ascii_question}'), SentenceTransformerFeatureExtractor(data))"""
        )
        .limit(3)
        .select("data")
        .df()
    )

    # Merge all context information.
    context = "; \n".join(context_docs["story_table.data"])

    # LLM
    messages = [
        {"role": "user", "content": f"Here is some context:{context}"},
        {
            "role": "user",
            "content": f"Answer this question based on context: {question}",
        },
    ]
    llm.chat_completion(messages)


def main():
    path = download_story()

    ask_question(path)


if __name__ == "__main__":
    main()
