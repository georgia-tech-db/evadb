from time import perf_counter

from util import download_story, read_text_line

from eva.interfaces.relational.db import EVAConnection, connect
from eva.udfs.udf_bootstrap_queries import Text_feat_udf_query


def ask_question(path):
    conn = connect()

    conn.query(Text_feat_udf_query).execute()

    try: 
        conn.query("DROP TABLE IF EXISTS TablePPText;").execute()
    except Exception:
        pass

    try: 
        conn.query("DROP TABLE IF EXISTS FeatTablePPText;").execute()
    except Exception:
        pass

    conn.query("CREATE TABLE TablePPText (id INTEGER, data TEXT(1000));").execute()

    # Insert text chunk by chunk.
    for i, text in enumerate(read_text_line(path)):
        conn.query(f"INSERT INTO TablePPText (id, data) VALUES ({i}, '{text}');").execute()

    # Extract features from text.
    st = perf_counter()
    conn.query("""CREATE TABLE FeatTablePPText AS
        SELECT SentenceFeatureExtractor(data), data FROM TablePPText;""").execute()
    print(f"Feature extraction time: {(perf_counter() - st) * 1000:.3f} ms")

    # Create search index on extracted features.
    conn.query("CREATE INDEX TextIndex ON FeatTablePPText (features) USING FAISS;").execute()

    # Search similar text as the asked question.
    question = "Where does Bennet family live?"
    res_batch = conn.query(f"""SELECT data FROM FeatTablePPText
        ORDER BY Similarity(SentenceFeatureExtractor('{question}'), features)
        LIMIT 10;""").execute()



def main():
    path = download_story()

    ask_question(path)


if __name__ == "__main__":
    main()