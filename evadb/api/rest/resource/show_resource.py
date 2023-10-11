from flask_restful import Resource, abort
from evadb.api.rest.start import cursor
from http import HTTPStatus
from flask import request

class showResource(Resource):
    def get(self):
        query = """ 
            SHOW FUNCTIONS
        """

        res = cursor.query(query).df()
        return {"msg" : "SHOW succeed" , "response" : res.to_json()}