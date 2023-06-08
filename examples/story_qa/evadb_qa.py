from gpt4all import GPT4All
from time import perf_counter

from util import download_story, text_splitter, try_execute

import evadb


def ask_question(path):
    # Initialize early to exlcude download time.
    llm = GPT4All("ggml-gpt4all-j-v1.3-groovy")

    cursor = evadb.connect().cursor()
    
    story_table = f"TablePPText"
    story_feat_table = f"FeatTablePPText"
    index_table = f"IndexTable"

    cursor.drop_udf("SentenceFeatureExtractor;").execute()
    cursor.create_udf("SentenceFeatureExtractor", impl_path="evadb/udfs/sentence_feature_extractor.py").execute()

    cursor.drop_table(story_table)
    cursor.drop_table(story_feat_table)
    
    print("Create table")

    cursor.query(f"CREATE TABLE {story_table} (id INTEGER, data TEXT(1000));").execute()

    # Insert text chunk by chunk.
    for i, text in enumerate(text_splitter(path)):
        cursor.query(f"INSERT INTO {story_table} (id, data) VALUES ({i}, '{text}');").execute()

    print("Extract features")

    # Extract features from text.
    st = perf_counter()
    cursor.query(f"""CREATE TABLE {story_feat_table} AS
        SELECT SentenceFeatureExtractor(data), data FROM {story_table};""").execute()
    fin = perf_counter()

    print("Create index")

    # Create search index on extracted features.
    cursor.create_vector_index(index_table, story_feat_table, "features", "FAISS")

    print("Query")
    
    # Search similar text as the asked question.
    question = "Who is Prince Boris Drubetskoy?"
    res_batch = cursor.query(f"""SELECT data FROM { } 
        ORDER BY Similarity(SentenceFeatureExtractor('{question}'), features)
        LIMIT 5;""").execute()
    
    print("Merge")

    # Merge all context information.
    context_list = []
    for i in range(len(res_batch)):
        context_list.append(res_batch.frames[f"{story_feat_table.lower()}.data"][i])
    context = ";".join(context_list)

    print("LLM")

    # LLM
    messages = [
        {"role": "user", "content": f"Here is some context:{context}"},
        {"role": "user", "content": f"Answer this question based on context: {question}"},
    ]
    llm.chat_completion(messages)

    print(f"Feature extraction time: {(fin - st) * 1000:.3f} ms")
    print(f"Total QA time: {(perf_counter() - st) * 1000:.3f} ms")


def main():
    path = download_story()

    ask_question(path)


if __name__ == "__main__":
    main()