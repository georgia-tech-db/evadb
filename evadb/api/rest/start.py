from flask import Flask
from flask_restful import Api
from evadb.api.rest.resource.route import init_routes

app = Flask(__name__)
api = Api(app)

if __name__ == "__main__":
    init_routes(api, app)
    app.run(debug=True)         
