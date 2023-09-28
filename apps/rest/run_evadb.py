from flask import Flask
from flask_restful import Api, Resource
import evadb

app = Flask(__name__)
api = Api(app)

cursor = evadb.connect().cursor()

class DatabaseResource(Resource):
    def get(self,db_name):

        # Create a database
        query = """ CREATE DATABASE """ + db_name + """
            WITH ENGINE = 'postgres',
            PARAMETERS = {
                "user": "eva",
                "password": "password",
                "host": "localhost",
                "port": "5000",
                "database":""" + db_name + """
            }; """
        
        res = cursor.query(query).df()
        return {"msg" : "Created Database" , "response" : res.to_json()}

class TableResource(Resource):
    def get(self, name):
        query = """ 
            CREATE TABLE IF NOT EXISTS """ + name + """ (
                id INTEGER UNIQUE,
                label TEXT(30)
                    ); 
        """
        res = cursor.query(query).df()
        return {"msg" : "Created table ", "response" : res.to_json() }
    
    def post(self,name):
        query = """
                INSERT INTO """+ name + """ (id, label)
                VALUES (
                2,
                '7019462-Eva'
                );
        """
        res = cursor.query(query).df()
        return {"msg" : "Entry added to database" , "response" : res.to_json()}
    
    def delete(self,name):
        query = """
                DROP table """+ name +""";
            """
        res = cursor.query(query).df()
        return {"response" : res.to_json()}



api.add_resource(DatabaseResource, "/db/<string:name>")
api.add_resource(TableResource, "/table/<string:name>")


# GET UDFS
@app.route('/udfs', methods = ['GET'])
def udfs():
    res = cursor.query("SHOW UDFS;").df()
    return {"response" : res.to_json()}   

#GET FUNCTIONS
@app.route('/func', methods = ['GET'])
def func():
    res = cursor.query("SHOW FUNCTIONS;").df()
    return {"response" : res.to_json()}     

@app.route('/table_data/<name>',methods = ['GET'])
def get_data(name):
    query = "Select * from" + name + ";"
    res = cursor.query(query).df() #Show 
    return {"response" : res.to_json()}

@app.route('/query/<query>',methods = ['GET'])
def query_from_db(query):
    res = cursor.query(query).df() #Show 
    return {"response" : res.to_json()}

if __name__ == "__main__":
    app.run(debug=True)         