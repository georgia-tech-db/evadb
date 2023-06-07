import random

from gpt4all import GPT4All
from time import perf_counter

from util import download_story, read_text_line, try_execute

from eva.interfaces.relational.db import EVAConnection, connect
from eva.udfs.udf_bootstrap_queries import Text_feat_udf_query, Similarity_udf_query


def ask_question(path):
    # Initialize early to exlcude download time.
    llm = GPT4All("ggml-gpt4all-j-v1.3-groovy")

    conn = connect()

    conn.query(Text_feat_udf_query).execute()
    conn.query(Similarity_udf_query).execute()

    random_num = random.randint(0, 1000000)
    story_table = f"TablePPText{random_num}"
    story_feat_table = f"FeatTablePPText{random_num}"
    index_table = f"IndexTable{random_num}"

    try_execute(conn, f"DROP TABLE IF EXISTS {story_table};")
    try_execute(conn, f"DROP TABLE IF EXISTS {story_feat_table};")

    conn.query(f"CREATE TABLE {story_table} (id INTEGER, data TEXT(1000));").execute()

    # Insert text chunk by chunk.
    for i, text in enumerate(read_text_line(path)):
        conn.query(f"INSERT INTO {story_table} (id, data) VALUES ({i}, '{text}');").execute()

    # Extract features from text.
    st = perf_counter()
    conn.query(f"""CREATE TABLE {story_feat_table} AS
        SELECT SentenceFeatureExtractor(data), data FROM {story_table};""").execute()
    print(f"Feature extraction time: {(perf_counter() - st) * 1000:.3f} ms")

    # Create search index on extracted features.
    conn.query(f"CREATE INDEX {index_table} ON {story_feat_table} (features) USING FAISS;").execute()

    # Search similar text as the asked question.
    question = "Where does Bennet family live?"
    res_batch = conn.query(f"""SELECT data FROM {story_feat_table} 
        ORDER BY Similarity(SentenceFeatureExtractor('{question}'), features)
        LIMIT 5;""").execute()
    
    # Merge all context information.
    context_list = []
    for i in range(len(res_batch)):
        context_list.append(res_batch.frames[f"{story_feat_table.lower()}.data"][i])
    context = ";".join(context_list)

    # LLM
    messages = [
        {"role": "system", "content": f"Here is some context:{context}"},
        {"role": "user", "content": f"Answer this question based on context: {question}"},
    ]
    llm.chat_completion(messages)
    print(f"Total QA time: {(perf_counter() - st) * 1000:.3f} ms")


def main():
    path = download_story()

    ask_question(path)


if __name__ == "__main__":
    main()