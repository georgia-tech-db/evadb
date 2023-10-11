from flask_restful import Resource, abort
from evadb.api.rest.start import cursor
from http import HTTPStatus
from flask import request

class functionResource(Resource):
    def post(self, functionName):
        inputs = ""
        outputs = ""
        for key, value in request.json['input'].items():
            if inputs == "":
                inputs = key + ' ' + value
            else:
                inputs += ",\n" + key + " " + value
            
        for key, value in request.json['output'].items():
            if outputs == "":
                outputs = key + ' ' + value
            else:
                outputs += ",\n" + key + " " + value

        query = """ 
            CREATE FUNCTION IF NOT EXIST {}
            INPUT ({})
            OUTPUT ({})
            TYPE {}
            IMPL {}
        """.format(functionName, inputs, outputs, request.json['type'], request.json['IMPL'])

        res = cursor.query(query).df()
        return {"msg" : "CREATE succeed" , "response" : res.to_json()}

    def delete(self, functionName):
        query = """ 
            DROP FUNCTION {}
        """.format(functionName)

        res = cursor.query(query).df()
        return {"msg" : "DROP succeed" , "response" : res.to_json()}