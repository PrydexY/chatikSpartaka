from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import sqlite3
import datetime
from flask import request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chatik'
socketio = SocketIO(app)
black_list = ["10.10.10.130", "10.10.10.172"]


class data_base:
    def __init__(self):
        self.bd = sqlite3.connect('db.db', check_same_thread=False)
        self.cursor = self.bd.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        text TEXT NOT NULL,
        time timestamp
        )
        ''')

        self.bd.commit()

    def add_message(self, username, text):
        query = """INSERT INTO 'messages'
                             ('username', 'text', 'time')
                             VALUES (?, ?, ?);"""

        data_tuple = (username, text, datetime.datetime.now())
        self.cursor.execute(query, data_tuple)
        self.bd.commit()

    def get_messages(self):
        query = """SELECT * FROM messages;"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def close(self):
        self.bd.close()


messages = data_base()


@app.route('/')
def index():
    return render_template('index.html', old=messages.get_messages(), leng=len(messages.get_messages()))


@socketio.on('message')
def handle_message(message):
    message_text = message.split(", ")[1]
    name = message.split(", ")[0]
    messages.add_message(name, message_text)
    print(request.remote_addr, name)
    if not request.remote_addr in black_list:
        emit('message', "<b>" + name + "</b> ("+ str(datetime.datetime.now()) + ")<br><br>" + message_text, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, port=80, host='0.0.0.0', allow_unsafe_werkzeug=True)
    messages.close()
