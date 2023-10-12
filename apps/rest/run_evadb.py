from flask import Flask,flash, request, redirect,render_template
from flask_restful import Api
import os
from werkzeug.utils import secure_filename
import evadb
from pathlib import Path

cursor = evadb.connect().cursor()
cwd = os.getcwd()
UPLOAD_FOLDER = cwd + "/files"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)
app.secret_key = "evadb-rest-apis"

# Get Query response
@app.route('/query',methods = ['POST','GET'])
def query_from_db():
    if request.method == 'POST':
        query = request.form['query']
        print(query)
        res = cursor.query(query).df() 
        return {"response" : res.to_json()}
    return render_template('query.html')


# Upload file to server
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    
@app.route('/upload',methods = ['GET','POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file detected')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = Path(UPLOAD_FOLDER +"/"+ filename)
            print()
            if path.is_file():
                flash('File uploaded')
                return {"response":"File saved"}
            else:
                flash('Failed to upload file')
                return redirect(request.url)
    return render_template('upload.html')


if __name__ == "__main__":
    app.run(debug=True)         