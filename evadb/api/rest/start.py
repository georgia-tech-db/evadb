from flask import Flask
from flask_restful import Api
import evadb
from evadb.api.rest.resource.select_resource import selectResource
from evadb.api.rest.resource.load_resource import loadResource
from evadb.api.rest.resource.explain_resource import explainResource
from evadb.api.rest.resource.show_resource import showResource
from evadb.api.rest.resource.table_resource import tableResource
from evadb.api.rest.resource.function_resource import functionResource
from evadb.api.rest.resource.entry_resource import entryResource

app = Flask(__name__)
api = Api(app)

cursor = evadb.connect().cursor()

api.add_resource(selectResource, "/select/<string:tableName>")
api.add_resource(loadResource, "/load/<string:tableName>")
api.add_resource(explainResource, "/explain")
api.add_resource(showResource, "/show")
api.add_resource(tableResource, "/table/<string:tableName>")
api.add_resource(functionResource, "/function/<string:tableName>")
api.add_resource(entryResource, "/entry/<string:tableName>")

if __name__ == "__main__":
    app.run(debug=True)         
