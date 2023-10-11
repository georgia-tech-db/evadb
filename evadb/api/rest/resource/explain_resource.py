from flask_restful import Resource, abort
from evadb.api.rest.start import cursor
from http import HTTPStatus
from flask import request

class explainResource(Resource):
    def post(self):
        if 'query' not in request.json:
            abort(HTTPStatus.BAD_REQUEST, 'Must provide "query" parameter in POST body')

        query = """ 
            EXPLAIN {}
        """.format(query)

        res = cursor.query(query).df()
        return {"msg" : "EXPLAIN succeed" , "response" : res.to_json()}