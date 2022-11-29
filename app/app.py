from functools import wraps
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import Form
from wtforms import TextField
import asyncio
from flask import jsonify

def async_action(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our very hard to guess secretfir'

@app.route('/')
def index():
    return render_template('video.html')

# Simple form handling using raw HTML forms
@app.route('/search')
@async_action
async def enter():
    video_path = request.args.get('video_path')
    phrase = request.args.get('phrase') # request.form['phrase']
    # print('LOAD FILE \'{}\' INTO TranscriptVideo WITH FORMAT RICH_VIDEO'.format(video_path))
    # print(phrase)

    # EVA UPLOAD AND QUERY
    from eva.server.db_api import connect_async
    import asyncio

    video_pos = ""

    # nest_asynio doesn't work
    # workaround ref: https://stackoverflow.com/questions/55409641/asyncio-run-cannot-be-called-from-a-running-event-loop-when-using-jupyter-no
    # /Users/omkar/Downloads/ua_detrac.mp4, billion trillion

    async def query():
        connection = await connect_async(host='127.0.0.1', port=5432)
        cursor = connection.cursor()
        await cursor.execute_async('LOAD FILE \'{}\' INTO TranscriptVideo WITH FORMAT RICH_VIDEO'.format(video_path))
        await cursor.fetch_all_async()
        await cursor.execute_async(
            'SELECT p.start_time, p.end_time FROM (SELECT Phrases(2) FROM TranscriptVideo) as p WHERE p.phrase = "{}"'.format(phrase))
        return await cursor.fetch_all_async()

    loop = asyncio.get_running_loop()
    tsk = loop.create_task(query())

    for f in asyncio.as_completed([tsk]):
        result = await f
        print(result)
        for start in result.batch.frames['p.start_time']:
            time = int(start)
            return jsonify(time - 1)

    return jsonify('')

# More powerful approach using WTForms
class RegistrationForm(Form):
    first_name = TextField('First Name')
    last_name = TextField('Last Name')

# Run the application
app.run(debug=True)