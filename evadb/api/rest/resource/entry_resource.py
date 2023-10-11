from flask_restful import Resource, abort
from evadb.api.rest.resource.cursor import cursor
from http import HTTPStatus
from flask import request

class entryResource(Resource):
    def post(self, tableName, predicates):
        colNames = ""
        colValues = ""
        if 'value_to_insert' not in request.json:
            abort(HTTPStatus.BAD_REQUEST, 'Must provide "value_to_insert" parameter in POST body')
        for key, value in request.json['value_to_insert'].items():
            if colNames == "":
                colNames = key
            else:
                colNames += ", " + key
            if colValues == "":
                colValues = value
            else:
                colValues += ", " + value

        query = """ 
            INSERT INTO {} ({}) VALUES
                ({})
        """.format(tableName, colNames, colValues)
        res = cursor.query(query).df()

        return {"msg" : "INSERT succeed" , "response" : res.to_json()}

    def delete(self, tableName, predicates):
        query = """ 
            DELETE FROM {} WHERE {} 
        """.format(tableName, predicates)
        print(query)
        res = cursor.query(query).df()
        return {"msg" : "DELETE succeed" , "response" : res.to_json()}