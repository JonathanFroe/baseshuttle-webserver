from flask import Flask, redirect, url_for, render_template
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

import uuid
import logging

app = Flask(__name__, static_folder="static", static_url_path='')
app.config['SECRET_KEY'] = uuid.uuid4().hex
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

socketio = SocketIO(app, cors_allowed_origins=[
                    "https://baseshuttle.de", "https://www.baseshuttle.de", "http://127.0.0.1:5000", "http://192.168.178.59:5000"])

logging.basicConfig(format='%(asctime)s\t%(levelname)s:%(message)s',filename='info.log', level=logging.DEBUG)

from postsofcompliments import postsofcompliments
app.register_blueprint(postsofcompliments)

from formular import formular
app.register_blueprint(formular)

@app.route('/')
def index():
    return redirect(url_for('postsofcompliments.select'))
