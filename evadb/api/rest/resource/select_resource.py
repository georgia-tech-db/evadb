from flask_restful import Resource, abort
from evadb.api.rest.start import cursor
from http import HTTPStatus
from flask import request

class selectResource(Resource):
    def post(self, tableName):
        if 'columns' not in request.json:
            abort(HTTPStatus.BAD_REQUEST, 'Must provide "columns" parameter in POST body')
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
                query += "WHERE {}".format(request.json['where'])
            if('orderby' in request.json):
                query += "ORDER BY {}".format(request.json['orderBy'])

        res = cursor.query(query).df()
        return {"msg" : "SELECT succeed" , "response" : res.to_json()}