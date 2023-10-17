from flask_restful import Resource, reqparse
from evadb.api.rest.cursor import cursor

class tableResource(Resource):
    def post(self, tableName):
        parser = reqparse.RequestParser()
        parser.add_argument("columns", type=dict, required=True, help="column names and types should be provided as a dict")
        args = parser.parse_args()

        newCols = ""
        for key, value in args['columns'].items():
            if newCols == "":
                newCols = key + " " + value
            else:
                newCols += (",\n"+'                '+key+" "+value)
        
        query = """ 
            CREATE TABLE IF NOT EXISTS {}(
                {}
            )
        """.format(tableName, newCols)
        res = cursor.query(query).df()

        return {"msg" : "CREATE table succeed" , "response" : res.to_json()}

    def delete(self, tableName):
        query = """ 
            DROP TABLE IF EXISTS {}
        """.format(tableName)
        res = cursor.query(query).df()

        return {"msg" : "DROP table succeed" , "response" : res.to_json()}

    def put(self, tableName):
        parser = reqparse.RequestParser()
        parser.add_argument("new_name", type=str, required=True, help="new name of the table should be provided as a string")
        args = parser.parse_args()

        query = """ 
            RENAME TABLE {} TO {}
        """.format(tableName, args['new_name'])
        res = cursor.query(query).df()

        return {"msg" : "RENAME table succeed" , "response" : res.to_json()}