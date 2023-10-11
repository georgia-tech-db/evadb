from flask_restful import Resource, abort
from evadb.api.rest.start import cursor
from http import HTTPStatus
from flask import request

class loadResource(Resource):
    def post(self, tableName):
        if request.json['type'] == 'CSV':
            cols = ''
            for key, value in request.json['columns']:
                if cols == '':
                    cols = key + ' ' + value
                else:
                    cols += (',\n' + key + ' ' + value)
            query = """
            CREATE TABLE IF NOT EXIST {} (
            {}
            )
        """.format(tableName, cols)
        else:
            query = """ 
                LOAD {} {} INTO {}
            """.format(request.json['type'], request.json['path'], tableName)

        res = cursor.query(query).df()
        return {"msg" : "LOAD succeed" , "response" : res.to_json()}
