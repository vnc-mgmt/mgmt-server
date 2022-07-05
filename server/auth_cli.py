import hashlib
import sqlite3
import os
import codecs

class AuthenticationManagement:
    def __init__(self):
        self.db_name = 'data.sqlite'
        self.db = sqlite3.connect(self.db_name)
        cur = self.db.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, key TEXT, permissions INTEGER)')
        cur.close()
    def auth(self, username, passwd):
        cur = self.db.cursor()
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()
        cur.close()
        authenticated = False
        for user in users:
            if user[1] == username:
                hex_decoded = codecs.decode(user[2], 'hex_codec')
                salt = hex_decoded[:32]
                key = hex_decoded[32:]
                new_key = self.get_hash(passwd, salt)
                if new_key == key:
                    authenticated = int(user[3])
        return authenticated
    def get_user_details(self, username):
        cur = self.db.cursor()
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()
        cur.close()
        permissions = 0
        user_found = False
        for user in users:
            if user[1] == username:
                permissions = user[3]
                user_found = True
        return username, permissions, user_found
    def get_hash(self, passwd, salt):
        key = hashlib.pbkdf2_hmac(
            'sha256',
            passwd.encode('utf-8'),
            salt,
            100000
        )
        return key
    def add_user(self, username, passwd, permissions):
        cur = self.db.cursor()
        salt = os.urandom(32)
        hashed_passwd = self.get_hash(passwd, salt)
        cur.execute('INSERT INTO users VALUES(null, "{}", "{}", {})'.format(username, hashed_passwd, permissions))
        cur.close()
        self.db.commit()
