import uuid

from flask import Flask, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, join_room
from flask_sqlalchemy import SQLAlchemy

from random import choice, choices
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret-key-is-top-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
socketio = SocketIO(app, cors_allowed_origins=[
                    "https://baseshuttle.de", "https://www.baseshuttle.de", "http://127.0.0.1:5000"])
db = SQLAlchemy(app)


class User(db.Model):
    """ Database User """
    user_id = db.Column(db.String(36), primary_key=True, unique=True)
    username = db.Column(db.String(80), nullable=False)
    joined_group_id = db.Column(db.String(6), nullable=False)
    data = db.Column(db.Text, nullable=True)


class Group(db.Model):
    """ Database Groups """
    group_id = db.Column(db.String(6), primary_key=True)
    user_turntable = db.Column(db.Text, nullable=True)
    active_cards = db.Column(db.Text)


os.remove("data.sqlite3")
db.create_all()


@app.route('/')
def select():
    return render_template("select.html")


@app.route('/join', methods=['GET', 'POST'])
def join_game():
    if request.method == 'POST':
        return redirect(url_for('create_character', session_id=request.form['id']))
    elif request.args.get('id'):
        return redirect(url_for('create_character', session_id=request.args.get('id')))
    else:
        return render_template("join.html")


@app.route('/create', methods=['GET', 'POST'])
def create_game():
    card_counter = 20
    if request.method == 'POST':
        if "create" in request.form:
            session = Group(group_id=request.form['id'], active_cards=";".join(
                request.form['card_elements'].split('\n')))
            db.session.add(session)
            db.session.commit()
            print(request.form['id'] + " created")  # *temp
            return redirect(url_for('create_character', session_id=request.form['id']))
        if "refresh" in request.form:
            card_counter = int(request.form['card_counter'])
    session_id = ''.join(choice(ascii_uppercase) for i in range(6))
    card_elements = None
    with open('karten.list', 'r') as karten:
        card_elements = "\n".join(
            choices(karten.read().split("\n"), k=card_counter))
    url = request.host_url + "/join?id=" + session_id
    return render_template("create.html", card_elements=card_elements, session_id=session_id, url=url, card_counter=card_counter)


@app.route('/session/<session_id>/character', methods=['GET', 'POST'])
def create_character(session_id):
    if db.session.query(Group.group_id).filter_by(group_id=session_id).scalar() is None:
        return redirect(url_for('join_game'))
    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        while User.query.filter_by(user_id=unique_id).scalar() is not None:
            unique_id = str(uuid.uuid4())
        user = User(user_id=unique_id,
                    username=request.form['name'], joined_group_id=session_id)
        db.session.add(user)
        db.session.flush()
        session['name'] = user.username
        session['id'] = user.user_id
        session['session_id'] = session_id
        session['reload'] = False
        db.session.commit()
        return redirect(url_for('play', session_id=session_id, reload=False))
    #*look

    return render_template('character.html')


@app.route('/session/<session_id>')
def play(session_id):
    if session.get('reload', None) == True:
        return redirect(url_for('join_game'))
    session['reload'] = True
    if db.session.query(Group.group_id).filter_by(group_id=session_id).scalar() is None:
        return redirect(url_for('join_game'))
    if db.session.query(User.user_id).filter_by(user_id=session.get("id", None)).scalar() is None:
        return redirect(url_for('create_character', session_id=session_id))
    return render_template('play.html', my_id=session.get('id', None))


def socket_update(room):
    socketio.emit('update', room=room, broadcast=True)


@socketio.on('connect')
def connect():
    room = session.get('session_id', None)
    if User.query.filter_by(user_id=session.get('id')).first() is not None:
        join_room(room)
        group = Group.query.filter_by(
            group_id=session.get('session_id', None)).first()
        if group.user_turntable != None:
            group.user_turntable = ";".join(
                [group.user_turntable, session.get('id', None)])
        else:
            group.user_turntable = session.get('id', None)
        db.session.commit()
        socketio.emit('alert', session.get('name', None) +
                      ' has entered the session', room=room)
        socket_update(session.get('session_id', None))
    else:
        socketio.emit('redirect', url_for('create_character', session_id=room))


@socketio.on('disconnect')
def disconnect():
    User.query.filter_by(user_id=session.get('id', None)).delete()
    db.session.commit()
    group = Group.query.filter_by(
        group_id=session.get('session_id', None)).first()
    if group is not None:
        turntable = group.user_turntable
        if turntable is not None:
            turntable = turntable.split(";")
            turntable.remove(session.get('id', None))
            if len(turntable) > 0:
                if len(turntable) > 1:
                    group.user_turntable = ";".join(turntable)
                else:
                    group.user_turntable = turntable[0]
            else:
                group.user_turntable = None
        if User.query.filter_by(joined_group_id=session.get('session_id', None)).scalar() is None:
            print(group.group_id + "was closed")
            Group.query.filter_by(group_id=group.group_id).delete()
        db.session.commit()
        # *temp
        print(
            f"{session.get('name', None)} with the ID {session.get('id', None)} has disconnected")
        socket_update(session.get('session_id', None))


@socketio.on('get_turn')
def get_turn():
    group = Group.query.filter_by(
        group_id=session.get('session_id', None)).first()
    socketio.emit('turn', group.user_turntable.split(
        ";")[0], room=session.get('session_id', None))


@socketio.on('get_player')
def get_player():
    player_list = User.query.filter_by(
        joined_group_id=session.get('session_id', None)).all()
    player = []
    for element in player_list:
        player.append([element.user_id, element.username])
    socketio.emit('chose_player', player, room=session.get('session_id', None))


@socketio.on('get_cards')
def get_cards():
    cards = Group.query.filter_by(group_id=session.get(
        'session_id', None)).first().active_cards
    if cards is not None:
        cards = cards.split(";")
        socketio.emit('chose_card', len(cards),
                      room=session.get('session_id', None))
    else:
        socketio.emit('chose_card', 0, room=session.get('session_id', None))


@socketio.on('select_card')
def select_card(card_id):
    cards = Group.query.filter_by(group_id=session.get(
        'session_id', None)).first().active_cards
    cards = cards.split(";")
    socketio.emit('card_text', [session.get('id', None), cards[int(
        card_id)]], room=session.get('session_id', None))
    socket_update(session.get('session_id', None))


@socketio.on('select_player')
def select_player(msg):
    chosen_player = User.query.filter_by(user_id=msg[0]).first()
    if chosen_player.data != None:
        chosen_player.data = ";".join([chosen_player.data, msg[1]])
    else:
        chosen_player.data = msg[1]
    db.session.commit()
    cards = Group.query.filter_by(group_id=session.get(
        'session_id', None)).first().active_cards
    cards = cards.split(";")
    cards.remove(msg[1])
    if len(cards) > 0:
        Group.query.filter_by(group_id=session.get(
            'session_id', None)).first().active_cards = ";".join(cards)
    else:
        Group.query.filter_by(group_id=session.get(
            'session_id', None)).first().active_cards = None
    db.session.commit()
    group = Group.query.filter_by(
        group_id=session.get('session_id', None)).first()
    turntable = group.user_turntable
    turntable = turntable.split(";")
    turntable.append(turntable[0])
    turntable.remove(turntable[0])
    group.user_turntable = ";".join(turntable)
    db.session.commit()
    socket_update(session.get('session_id', None))


@socketio.on('get_data')
def get_data():
    user = User.query.filter_by(user_id=session.get('id', None)).first()
    if user.data is not None:
        socketio.emit('data', [user.user_id, user.data.split(
            ";")], room=session.get('session_id', None))
    else:
        socketio.emit('data', [user.user_id, None], room=session.get(
            'session_id', None))  # ? Vielleicht irgendetwas schönes


if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0')
