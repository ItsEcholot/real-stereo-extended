from flask import Flask, send_file
from flask_restful import Api
import logging

from api.controllers.rooms import RoomsController

# define path of the static frontend files
frontendPath: str = '../../../frontend/dist'

# disable request log in console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# create app
app: Flask = Flask(__name__, static_url_path='', static_folder=frontendPath)


# serve the index.html from the frontend
@app.route('/')
def index():
    try:
        return send_file(frontendPath + '/index.html')
    except FileNotFoundError:
        return 'index.html does not exist'


# register all api routes
api = Api(app, '/api')
api.add_resource(RoomsController, '/rooms')


# start the web server in a separate thread
def startApi():
    app.run('0.0.0.0', 8080)
