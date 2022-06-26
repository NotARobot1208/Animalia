import psycopg2
import uuid
import os
import hashlib

os.system(os.environ.get("COCKROACH_UPDATE_CMD"))

class User:
    '''
    An user in the system. Create an user from DB with
    User(id), or create it based on parameters with
    User(id, username, password, rating). Note that
    creating an user this way does NOT touch the database,
    but only creates a "virtual" user in memory. Do not
    make an user this way, this is only for internal use
    inside functions in this file.

    You can also get an User object by username with the
    following syntax: User(username="username_here")
    '''
    def __init__(self, id=None, username=None, password=None, rating=None, questions=None, correct_questions=None):
        if username and password and rating and questions and correct_questions:
            self.id = id
            self.username = username.lower()
            self.password = password
            self.rating = rating
            self.questions = questions
            self.correct_questions = correct_questions
        elif id:
            self.id = id
            info = run_query("SELECT username, password, rating, questions, correct_questions FROM users WHERE id=%s", (id,))[0]
            self.username = info[0].lower()
            self.password = info[1]
            self.rating = info[2]
            self.questions = info[3]
            self.correct_questions = info[4]
        elif username:
            self.username = username.lower()
            info = run_query("SELECT id, password, rating, questions, correct_questions FROM users WHERE username=%s", (username.lower(),))
            if len(info) == 0:
                self.id = -1
            elif info != None:
                info = info[0]
                self.id = info[0]
                self.password = info[1]
                self.rating = info[2]
                self.questions = info[3]
                self.correct_questions = info[4]
            else:
                self.id = -1
        return
    def __repr__(self):
        return "User(" + str(self.__dict__)[1:-1].replace(": ", "=") + ")"
    def update(self):
        '''
        Any changes in an User must be updated in the database.
        Otherwise, the changes have no effect. Example:
        u = User(42)
        u.rating += 100
        u.update()
        '''
        print("UPDATE users SET username=%s, password=%s, rating=%s, questions=%s, correct_questions=%s WHERE id=%s" % (self.username, self.password, self.rating, self.questions, self.correct_questions, self.id))
        run_query("UPDATE users SET username=%s, password=%s, rating=%s, questions=%s, correct_questions=%s WHERE id=%s", (self.username, self.password, self.rating, self.questions, self.correct_questions, self.id))


def init():
    '''
    Initialize a database connection
    '''
    db_url = os.getenv("DB_CONNECTION_STRING")
    conn = psycopg2.connect(db_url)
    return conn

def run_query(cmd, args=()):
    '''
    Wrapper for running SQL commands. Will return a
    value if the query returns a value.

    '''
    conn = init()
    cur = conn.cursor()
    cur.execute(cmd, args)
    conn.commit()
    try:
        rows = cur.fetchall()
        conn.close()
        return rows
    except:
        conn.close()
        return

def seed_db():
    '''
    Creates the neccesary tables in the database.
    '''
    run_query("CREATE TABLE IF NOT EXISTS users (id BIGINT PRIMARY KEY, username STRING, password STRING, rating BIGINT, questions BIGINT, correct_questions BIGINT)")

def reset_db():
    '''
    Clears all information in the database
    '''
    run_query("DROP TABLE users")
    seed_db()

def gen_uid(username):
    '''
    Generates an user ID based on the username
    '''
    return int(hashlib.sha256(b"\x42\x42\x13\x37" + username.lower().encode()).hexdigest()[:15], 16)

def create_user(username, password, rating=1000):
    '''
    Creates an user in the database and returns a corresponding
    User() object.
    '''
    username = username.lower()
    id = gen_uid(username)
    run_query("INSERT INTO users (id, username, password, rating, questions, correct_questions) VALUES (%s, %s, %s, %s, %s, %s)", args=(id, username, password, rating, 0, 0))
    return User(id, username, password, rating)

def get_all_users():
    info = run_query("SELECT id, username, password, rating, questions, correct_questions from users")
    if info:
        return [User(item[0], item[1], item[2], item[3], item[4], item[5]) for item in info]
    else:
        return []
