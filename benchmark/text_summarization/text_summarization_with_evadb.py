import evadb
import time

cursor = evadb.connect().cursor()


cursor.query("DROP TABLE IF EXISTS cnn_news_test;").df()
cursor.query("""
    CREATE TABLE IF NOT EXISTS cnn_news_test(
        id TEXT(128),
        article TEXT(4096),
        highlights TEXT(1024)
    );""").df()
cursor.load('./cnn_news_test.csv', 'cnn_news_test', format="CSV").df()

cursor.query("DROP FUNCTION IF EXISTS TextSummarizer;").df()
cursor.query("""CREATE UDF IF NOT EXISTS TextSummarizer
                TYPE HuggingFace
                TASK 'summarization'
                MODEL 'sshleifer/distilbart-cnn-12-6'
                MIN_LENGTH 5
                MAX_LENGTH 100;""").df()


cursor.query("DROP TABLE IF EXISTS cnn_news_summary;").df()

cursor._evadb.config.update_value("executor", "batch_mem_size", 300000)
cursor._evadb.config.update_value("executor", "gpu_ids", [0,1])
cursor._evadb.config.update_value("experimental", "ray", True)

start_time = time.perf_counter()
cursor.query("""
    CREATE TABLE IF NOT EXISTS cnn_news_summary AS
    SELECT TextSummarizer(article) FROM cnn_news_test;""").df()
end_time = time.perf_counter()
print(f"{end_time-start_time:.2f} seconds")



