import sqlite3
import datetime


class messages_data_base:
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
        query = """SELECT * FROM messages ORDER BY time DESC;"""
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def close(self):
        self.bd.close()
