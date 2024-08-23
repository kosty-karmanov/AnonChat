import sqlite3
import datetime


def get_timestamp() -> int:
    return int(datetime.datetime.now().timestamp())


class Database:
    def __init__(self) -> None:
        self.con = sqlite3.connect("main.db")
        self.cur = self.con.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users(
                                id INTEGER, 
                                status INTEGER, 
                                companion INTEGER
                        )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS dialogues(
                                id1 INTEGER, 
                                id2 INTEGER, 
                                timestamp INTEGER
                        )''')

    def get_companion(self, id_: int) -> int:
        self.cur.execute('''SELECT companion FROM users WHERE id = ?''', (id_,))
        return self.cur.fetchall()[0][0]

    def get_status(self, id_: int) -> int:
        self.cur.execute('''SELECT status FROM users WHERE id = ?''', (id_,))
        return self.cur.fetchall()[0][0]

    def add_user(self, id_: int) -> None:
        self.cur.execute('''INSERT INTO users VALUES (?, 0, 0)''', (id_,))
        self.con.commit()

    def is_in_data_base(self, id_: int) -> bool:
        self.cur.execute('''SELECT id FROM users WHERE id = ?''', (id_,))
        return len(self.cur.fetchall()) > 0

    def set_finding(self, id_: int) -> None:
        self.cur.execute('''UPDATE users SET status = 1, companion = 0 WHERE id = ?''', (id_,))
        self.con.commit()

    def set_chatting(self, id_: int, comp: int) -> None:
        self.cur.execute('''UPDATE users SET status = 2, companion = ? WHERE id = ?''', (comp, id_,))
        self.con.commit()

    def set_afk(self, id_: int) -> None:
        self.cur.execute('''UPDATE users SET status = 0, companion = 0 WHERE id = ?''', (id_,))
        self.con.commit()

    def add_dialog(self, id1: int, id2: int) -> None:
        self.cur.execute('''INSERT INTO dialogues VALUES (?,?,?)''', (id1, id2, get_timestamp()))
        self.con.commit()

    def clean_dialogs(self) -> None:
        key_point = get_timestamp() - 3600
        self.cur.execute('''DELETE FROM dialogues WHERE timestamp < ?''', (key_point,))
        self.con.commit()

    def count_finders(self, id_: int):
        self.cur.execute('''SELECT id FROM users WHERE status = 1 AND id != ?''', (id_,))
        return len(self.cur.fetchall())

    def find_companion(self, id_: int) -> int:
        self.cur.execute(
            '''SELECT users.id 
                     FROM users 
                     LEFT JOIN dialogues 
                        ON users.id = dialogues.id1 AND dialogues.id2 = ? 
                     WHERE users.id != ? AND dialogues.id1 IS NULL AND status = 1 
                     ORDER BY RANDOM() 
                     LIMIT 1''',
            (id_, id_))
        data = self.cur.fetchall()
        if len(data) == 0:
            return -1
        return data[0][0]
