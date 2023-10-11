from flask import Flask, Response
from flask_restful import Api, request
import sys
sys.path.append('/Users/ethanyang/Documents/GitHub/evadb')
from evadb.api.rest.resource.table_resource import tableResource
from evadb.api.rest.resource.function_resource import functionResource
from evadb.api.rest.resource.entry_resource import entryResource
from evadb.api.rest.resource.cursor import cursor

app = Flask(__name__)
api = Api(app)

api.add_resource(tableResource, "/table/<string:tableName>")
api.add_resource(functionResource, "/function/<string:functionName>")
api.add_resource(entryResource, "/entry/<string:tableName>/<string:predicates>")

def gen_chunks(json_data, chunk_size=100):
    start = 0
    end = chunk_size
    while start < len(json_data):
        yield json_data[start:end].encode('utf-8')
        start = end
        end += chunk_size

@app.route('/show',methods = ['GET'])
def show_functions():
    query = """ 
        SHOW FUNCTIONS
    """
    print(query)
    res = cursor.query(query).df()
    return {"msg" : "SHOW succeed" , "response" : res.to_json()}

@app.route('/explain',methods = ['POST'])
def explain_query():
    query = """ 
        EXPLAIN {}
    """.format(request.json['query'])
    print(query)

    res = cursor.query(query).df()
    return {"msg" : "EXPLAIN succeed" , "response" : res.to_json()}

@app.route('/load/<tableName>', methods = ['POST'])
def load_files(tableName):
    if request.json['type'] == 'CSV':
        cols = ''
        for key, value in request.json['columns'].items():
            if cols == '':
                cols = key + ' ' + value
            else:
                cols += (',\n' +'        '+ key + ' ' + value)
        query = """
        CREATE TABLE IF NOT EXISTS {} (
        {}
        )
        """.format(tableName, cols)
        print(query)
        cursor.query(query).df()
        query = "LOAD CSV {} INTO {}".format(request.json['path'], tableName)
    else:
        query = """ 
            LOAD {} {} INTO {}
        """.format(request.json['type'], request.json['path'], tableName)
    print(query)
    res = cursor.query(query).df()
    return {"msg" : "LOAD succeed" , "response" : res.to_json()}

@app.route('/select/<tableName>', methods = ['POST'])
def post(tableName):
    cols = request.json['columns']
    cols = ', '.join(cols)
    
    if tableName == "none":
        query = "SELECT {}".format(cols)
    else:
        query = """ 
            SELECT {}
            FROM {}\n
        """.format(cols, tableName)
        if('where' in request.json):
            query += "    WHERE {}".format(request.json['where'])
        if('orderby' in request.json):
            query += "    ORDER BY {}".format(request.json['orderBy'])
    print(query)
    res = cursor.query(query).df()
    return Response(gen_chunks(res.to_json()), content_type='application/json', status=200, direct_passthrough=True)


if __name__ == "__main__":
    app.run(debug=True)         
