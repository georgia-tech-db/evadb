from flask_restful import Resource, abort
from evadb.api.rest.resource.cursor import cursor
from http import HTTPStatus
from flask import request

class tableResource(Resource):
    def post(self, tableName):
        newCols = ""
        cols = request.json['columns']
        for key, value in cols.items():
            if newCols == "":
                newCols = key + " " + value
            else:
                newCols += (",\n"+'                '+key+" "+value)
        
        query = """ 
            CREATE TABLE IF NOT EXISTS {}(
                {}
            )
        """.format(tableName, newCols)
        print(query)
        res = cursor.query(query).df()
        return {"msg" : "SELECT succeed" , "response" : res.to_json()}

    def delete(self, tableName):
        query = """ 
            DROP TABLE IF EXISTS {}
        """.format(tableName)

        res = cursor.query(query).df()
        return {"msg" : "DROP succeed" , "response" : res.to_json()}

    def put(self, tableName):
        query = """ 
            RENAME TABLE {} TO {}
        """.format(tableName, request.json['new_name'])

        res = cursor.query(query).df()
        return {"msg" : "RENAME succeed" , "response" : res.to_json()}