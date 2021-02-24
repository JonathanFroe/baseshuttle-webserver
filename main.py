from flask import Flask, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

socketio = SocketIO(app, cors_allowed_origins=[
                    "https://baseshuttle.de", "https://www.baseshuttle.de", "http://127.0.0.1:5000"])

from postsofcompliments import postsofcompliments

app.register_blueprint(postsofcompliments)

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0') #This is only for testing
