from flask import Response
from flask_restful import reqparse
from evadb.api.rest.resource.table import tableResource
from evadb.api.rest.resource.function import functionResource
from evadb.api.rest.resource.entry import entryResource
from evadb.api.rest.cursor import cursor

def gen_chunks(json_data, chunk_size=100):
    start = 0
    end = chunk_size
    while start < len(json_data):
        yield json_data[start:end].encode('utf-8')
        start = end
        end += chunk_size

def init_routes(api, app):
    api.add_resource(tableResource, "/api/table/<string:tableName>")
    api.add_resource(functionResource, "/api/function/<string:functionName>")
    api.add_resource(entryResource, "/api/entry/<string:tableName>/<string:predicates>", "/api/entry/<string:tableName>")

    @app.route('/api/show',methods = ['GET'])
    def show_functions():
        query = """ 
            SHOW FUNCTIONS
        """
        print(query)
        res = cursor.query(query).df()
        return {"msg" : "SHOW succeed" , "response" : res.to_json()}

    @app.route('/api/explain',methods = ['POST'])
    def explain_query():
        parser = reqparse.RequestParser()
        parser.add_argument("query", type=str, required=True, help="query to be explained should be a string")
        args = parser.parse_args()

        query = """ 
            EXPLAIN {}
        """.format(args['query'])
        res = cursor.query(query).df()

        return {"msg" : "EXPLAIN succeed" , "response" : res.to_json()}

    @app.route('/api/load/<tableName>', methods = ['POST'])
    def load_files(tableName):
        parser = reqparse.RequestParser()
        parser.add_argument("type", type=str, required=True, help="file type should be a string")
        parser.add_argument("columns", type=dict, required=False, help="columns should be provided as a dict if the file type is CSV")
        parser.add_argument("path", type=str, required=True, help="file path should be a string")
        args = parser.parse_args()

        if args['type'] == 'CSV':
            cols = ''
            for key, value in args['columns'].items():
                if cols == '':
                    cols = key + ' ' + value
                else:
                    cols += (',\n' +'        '+ key + ' ' + value)
            query = """
            CREATE TABLE IF NOT EXISTS {} (
            {}
            )
            """.format(tableName, cols)
            cursor.query(query).df()
            query = "LOAD CSV {} INTO {}".format(args['path'], tableName)
        else:
            query = """ 
                LOAD {} {} INTO {}
            """.format(args['type'], args['path'], tableName)
        res = cursor.query(query).df()

        return {"msg" : "LOAD succeed" , "response" : res.to_json()}

    @app.route('/api/select/<tableName>', methods = ['POST'])
    @app.route('/api/select', methods = ['POST'])
    def post(tableName):
        parser = reqparse.RequestParser()
        parser.add_argument("columns", type=list, required=True, help="columns in the SELECT query should be provided as a list")
        parser.add_argument("where", type=str, help="where clause should be provided as a string")
        parser.add_argument("orderBy", type=str, help="order by clause should be provided as a string")
        args = parser.parse_args()

        cols = args['columns']
        cols = ', '.join(cols)
        
        if tableName == "none":
            query = "SELECT {}".format(cols)
        else:
            query = """ 
                SELECT {}
                FROM {}\n
            """.format(cols, tableName)
            if('where' in args.keys()):
                query += "    WHERE {}".format(args['where'])
            if('orderby' in args.keys()):
                query += "    ORDER BY {}".format(args['orderBy'])
        res = cursor.query(query).df()

        return Response(gen_chunks({'msg': "SELECT succeed", "response":res.to_json}), content_type='application/json', status=200, direct_passthrough=True)
