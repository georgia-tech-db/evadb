from evadb.server.command_handler import execute_query_fetch_all
from evadb.configuration import constants


class CostEstimatorUtils():

    def fetch_table_stats(db, query):
        query_result = execute_query_fetch_all(
            db, query, do_not_print_exceptions=False, do_not_raise_exceptions=True
        )
        for _, row in query_result.iterrows():
            entry = {
                'table_name': row['table_stats.table_name'],
                'num_rows': row['table_stats.num_rows'],
                'hist': row['table_stats.hist']
            }
            constants.EVADB_STATS[row['table_stats.table_name']] = entry