from flask_restful import Resource, reqparse
from evadb.api.rest.cursor import cursor

class functionResource(Resource):
    def post(self, functionName):
        parser = reqparse.RequestParser()
        parser.add_argument("input", type=dict, required=True, help="input list of the function should be provided as a dict")
        parser.add_argument("output", type=dict, required=True, help="output list of the function should be provided as a dict")
        parser.add_argument("type", type=str, required=True, help="type of the function should be provided as a string")
        parser.add_argument("impl", type=str, required=True, help="imlp path of the function should be provided as a string")
        args = parser.parse_args()

        inputs = ""
        outputs = ""

        for key, value in args['input'].items():
            if inputs == "":
                inputs = key + ' ' + value
            else:
                inputs += ",\n" +'                '+ key + " " + value
            
        for key, value in args['output'].items():
            if outputs == "":
                outputs = key + ' ' + value
            else:
                outputs += ",\n" +'                ' + key + " " + value

        query = """ 
            CREATE FUNCTION IF NOT EXISTS {}
            INPUT ({})
            OUTPUT ({})
            TYPE {}
            IMPL {}
        """.format(functionName, inputs, outputs, args['type'], args['impl'])
        res = cursor.query(query).df()

        return {"message" : "CREATE function executed" , "response" : res.to_json()}

    def delete(self, functionName):
        query = """ 
            DROP FUNCTION IF EXISTS {}
        """.format(functionName)

        res = cursor.query(query).df()
        return {"message" : "DROP function executed" , "response" : res.to_json()}