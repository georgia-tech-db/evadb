from flask_restful import Resource, reqparse
from evadb.api.rest.cursor import cursor

class entryResource(Resource):
    def post(self, tableName):
        parser = reqparse.RequestParser()
        parser.add_argument("value_to_insert", type=dict, required=True, help="values to insert should be provided as a dict")
        args = parser.parse_args()

        colNames = ""
        colValues = ""

        for key, value in args['value_to_insert'].items():
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

        return {"msg" : "INSERT entry succeed" , "response" : res.to_json()}

    def delete(self, tableName, predicates):
        
        query = """ 
            DELETE FROM {} WHERE {} 
        """.format(tableName, predicates)
        res = cursor.query(query).df()

        return {"msg" : "DELETE entry succeed" , "response" : res.to_json()}