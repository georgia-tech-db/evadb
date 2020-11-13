import asyncio
import string
import random
import time

from src.server.client import EvaClient, start_client
from src.models.server.response import Response
from src.configuration.configuration_manager import ConfigurationManager

class EVAConnection:
    def __init__(self, protocol):
        self._protocol = protocol
    
    def cursor(self):
        return EVACursor(self._protocol)

class EVACursor:

    query_result = None

    def __init__(self, protocol):
        self.valid = True
        self.next_chunk = 0
        self._protocol = protocol
        self.next_row = 0

    async def execute (self, query):
        self._protocol._response_chunks = []
        self._protocol.send_message(query)
        print("Message Sent")
        while len(self._protocol._response_chunks) == 0:
            await asyncio.sleep(2)

        segs = self._protocol._response_chunks[0].split('|', 1)
        result_length = int(segs[0])
        self.query_result = segs[1]
        next_chunk = 1
        while len(self.query_result) < result_length:
            while len(self._protocol._response_chunks) <= next_chunk:
                await asyncio.sleep(2)
            self.query_result += self._protocol._response_chunks[next_chunk]
            next_chunk += 1

    def fetch_one(self):
        r = Response.from_json(self.query_result)
        row_data = r._batch._frames.loc[self.next_row]
        return row_data
    

async def connect (host: string, port: int, max_retry_count: int):
    loop = asyncio.get_event_loop()

    retries = max_retry_count * [1]

    while True:
        try:
            transport, protocol = await loop.create_connection(EvaClient, host, port)
        
        except Exception as e:
            if not retries:
                raise e 
            time.sleep(retries.pop(0) - random.random())
        else: 
            break
    
    return EVAConnection(protocol)

###USAGE###
'''
async def run(query:string):
    config = ConfigurationManager()
    hostname = config.get_value('server', 'host')
    port = config.get_value('server', 'port')

    loop = asyncio.get_event_loop() 
    connection = await connect(hostname, port,2)
    cursor = connection.cursor()
    await cursor.execute(query)
    #cursor.fetch_one()

asyncio.run(run('LOAD DATA INFILE "data/ua_detrac/ua_detrac.mp4" INTO MyVideo;'))
asyncio.run(run('SELECT id,data FROM MyVideo WHERE id < 5;'))
'''




    