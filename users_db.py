import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class UsersDB:
    def __init__(self):
        self.connection = sqlite3.connect("users_db.db")
        self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()
        self.init_db()
    
    def init_db(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER NOT NULL,
            email TEXT,
            firstname TEXT,
            lastname TEXT,
            phone INTEGER,
            passHash TEXT,
            PRIMARY KEY(id))"""
        )


    def insertUser(self, email, firstname, lastname, phone, passHash):
        data = [email, firstname, lastname, phone, passHash]
        self.cursor.execute("INSERT INTO users (email, firstname, lastname, phone, passHash) VALUES (?, ?, ?, ?, ?)", data)
        self.connection.commit()

    def retrieveUsers(self):
        self.cursor.execute("SELECT * FROM users")
        result = self.cursor.fetchall()
        return result

    def retrieveOneUser(self, user_id):
        data = [user_id]
        self.cursor.execute("SELECT * FROM users WHERE id = ?", data)
        result = self.cursor.fetchone()
        return result

    def deleteUser(self, user_id):
        data = [user_id]
        self.cursor.execute("DELETE FROM users WHERE id = ?", data)
        self.connection.commit()

    def updateUser(self, user_id, email, password, firstname, lastname, phone):
        print("UPDATE USER", user_id, email, password, firstname, lastname, phone)

        #print(update_str)
        #self.cursor.execute("UPDATE table_name SET column1 = value1, column2 = value2...., columnN = valueN WHERE [condition];", data)
        self.connection.execute("""
            UPDATE users SET email = ?,
            passHash = ?, firstname = ?,
            lastname = ?,
            phone = ?
            WHERE id = ?
            """, (email, password, firstname, lastname, phone, int(user_id)))
        self.connection.commit()

    def getPassHash(self, email):
        email = [email]
        self.cursor.execute("SELECT passHash FROM users WHERE email = ?", email)
        passhash = self.cursor.fetchone()["passHash"]
        #print("passhash", passhash)
        return passhash

    def doesEmailExist(self, email) -> bool:
        email = [email]
        self.cursor.execute("SELECT email FROM users WHERE email = ?", email)
        exist = self.cursor.fetchone()
        return False if exist is None else True
    
    def getUserFromEmail(self, email):
        email = [email]
        self.cursor.execute("SELECT * FROM users WHERE email = ?", email)
        return self.cursor.fetchone()

