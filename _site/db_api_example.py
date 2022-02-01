import asyncio
import sys

from typing import List
from eva.server.db_api import connect, connect_async

async def run_async(query: List[str]):
    hostname = '0.0.0.0'
    port = 5432

    connection = await connect_async(hostname, port)
    cursor = connection.cursor()
    for onequery in query:
        await cursor.execute_async(onequery)
        response = await cursor.fetch_one_async()
        print('Query: %s' % onequery)
        print(response)

def run(query: List[str]):
    hostname = '0.0.0.0'
    port = 5432

    connection = connect(hostname, port)
    cursor = connection.cursor()
    for onequery in query:
        cursor.execute(onequery)
        response = cursor.fetch_one()
        print('Query: %s' % onequery)
        print(response)

if __name__ == '__main__':
    queries = ['INVALID QUERY',
               'UPLOAD INFILE "data/ua_detrac/ua_detrac.mp4" \
                       PATH "test_video.mp4";',
               'LOAD DATA INFILE "test_video.mp4" INTO MyVideo;',
               'SELECT id,data FROM MyVideo WHERE id < 5;']

    if sys.argv[1] != 'sync':
        asyncio.run(run_async(queries))
    else:
        run([queries])

