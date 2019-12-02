from session_store import SessionStore

from http.server import BaseHTTPRequestHandler, HTTPServer
from http import cookies
import ssl
from passlib.hash import argon2
from urllib.parse import parse_qs
from users_db import UsersDB
import argparse
import json


SESSION_STORE = SessionStore()


def argon2_hash(plaintext: str) -> str:
    h = argon2.hash(plaintext)
    return h


def argon2_verify(plainpass: str, hashpass: argon2_hash) -> bool:
    return argon2.verify(plainpass, hashpass)


class MyRequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        self.send_cookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)

    def load_cookie(self):
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()

    def send_cookie(self):
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())

    def load_session(self):

        self.load_cookie()

        # if session ID is in the cookie
        if "sessionId" in self.cookie:
            sessionId = self.cookie["sessionId"].value

            # save the session into self.session for use later
            self.session = SESSION_STORE.getSession(sessionId)

            if self.session == None:
                # create a new session
                sessionId = SESSION_STORE.createSession()
                self.session = SESSION_STORE.getSession(sessionId)

                # set the new session ID into the cookie
                self.cookie["sessionId"] = sessionId
        # otherwise, if session ID is NOT in the cookie
        else:
            # create a new session
            sessionId = SESSION_STORE.createSession()
            self.session = SESSION_STORE.getSession(sessionId)

            # set the new session ID into the cookie
            self.cookie["sessionId"] = sessionId
        print(self.session)

    def do_OPTIONS(self):
        self.load_session()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self.load_session()

        """
        if self.path == "/hello":
            self.send_response(200)
            self.send_header("Set-Cookie", "type=Chocolate")
            self.send_header("Set-Cookie", "type=Huge")
            self.end_headers()
        """

        if self.path == "/users":
            self.handleUserRetrieveCollection()
        elif self.path.startswith("/users/"):
            self.handleUserRetrieveMember()
        elif self.path.startswith("/sessions"):
            self.handleCheckSession()
        else:
            self.respond404()

    def do_POST(self):
        self.load_session()

        if self.path == "/users":
            self.handleUserCreate()
        elif self.path.startswith("/sessions"):
            self.handleSignIn()
        elif self.path.startswith("/tools/"):
            self.handleVerifyEmail()
        else:
            self.respond404()

    def do_DELETE(self):
        self.load_session()

        if self.path.startswith("/users"):
            self.handleUserDelete()
        else:
            self.respond404()

    def do_PUT(self):
        self.load_session()
        print("put triggered")

        if self.path.startswith("/users/"):
            self.handleUserUpdate()
        else:
            self.respond404()

    def handleUserRetrieveMember(self):
        if "userId" not in self.session:
            self.respond401()
            return
        parts = self.path.split("/")
        user_id = parts[2]

        db = UsersDB()
        user = db.retrieveOneUser(user_id)

        if user is not None:
            self.send_header("Content-Type", "application/json")
            self.wfile.write(bytes(json.dumps(user), "utf-8"))
            self.respond200()
        else:
            self.respond404()

    def handleUserRetrieveCollection(self):
        if "userId" not in self.session:
            self.respond401()
            return

        self.send_response(200)  # 200 OK
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        db = UsersDB()
        users = db.retrieveUsers()
        self.wfile.write(bytes(json.dumps(users), "utf-8"))

    def handleUserCreate(self):
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsed_body = parse_qs(body)
        db = UsersDB()

        if db.doesEmailExist(parsed_body["email"][0]):
            # user with that email already exists
            self.respond409()
        else:
            firstname = parsed_body["firstName"][0]
            lastname = parsed_body["lastName"][0]
            email = parsed_body["email"][0]
            phone = parsed_body["phone"][0]

            pass_plain = parsed_body["password"][0]
            pass_hash = argon2_hash(pass_plain)
            pass_plain = None

            db.insertUser(email, firstname, lastname, phone, pass_hash)

            self.respond201()

    def handleUserDelete(self):
        if "userId" not in self.session:
            self.respond401()
            return

        parts = self.path.split("/")
        user_id = parts[2]

        db = UsersDB()
        user = db.retrieveOneUser(user_id)

        if user is not None:
            db.deleteUser(user_id)
            self.send_response(200)  # 200 OK
            self.end_headers()
        else:
            self.respond404()

    def handleUserUpdate(self):
        if "userId" not in self.session:
            self.respond401()
            return



        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("BODY (string):", body)

        parsed_body = parse_qs(body)
        parts = self.path.split("/")
        user_id = parts[2]

        db = UsersDB()
        user = db.retrieveOneUser(user_id)

        if user is not None:
            db.updateUser(
                user_id,
                parsed_body["email"][0],
                argon2_hash(parsed_body["password"][0]),
                parsed_body["firstName"][0],
                parsed_body["lastName"][0],
                parsed_body["phone"][0]
            )
            self.respond200()
        else:
            self.respond404()

    def handleVerifyEmail(self):
        parts = self.path.split("/")
        email = parts[2]
        db = UsersDB()

        if db.doesEmailExist(email):
            print(409)
            self.respond409()
        else:
            print(200)
            self.respond200()

    def handleCheckSession(self):
        if "userId" not in self.session:
            print("userid not in session")
            self.respond401()
            return

        db = UsersDB()
        user = db.retrieveOneUser(self.session["userId"])
       # print(user)
        if user is not None:
            self.wfile.write(bytes(json.dumps(user["firstname"]), "utf-8"))
            self.respond200()

    def handleSignIn(self):
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsed_body = parse_qs(body)
        db = UsersDB()

        try:
            pass_attempt = parsed_body["password"][0]
            email_attempt = parsed_body["email"][0]
        except KeyError:
            self.respond400()
            return
    
        dbhash = db.getPassHash(email_attempt)
        print("dbhash", dbhash)
        
        user = db.getUserFromEmail(email_attempt)

        if db.doesEmailExist(email_attempt) and dbhash is not None:
            print("email exists")
            pass_matches = argon2_verify(pass_attempt, dbhash)
            if pass_matches:
                print("hash matches")
                self.session["userId"] = user["id"]
                self.respond200()
                self.wfile.write(bytes(json.dumps(user["firstname"]), "utf-8"))

            else:
                print("hash doesnt match")
                self.respond401()
        else:
            print("email doesnt exit")
            self.respond401()


    def respond200(self):
        """200 OK"""
        self.send_response(200)
        self.end_headers()

    def respond201(self):
        """201 Created"""
        self.send_response(201)
        self.end_headers()

    def respond400(self):
        """400 Bad Request"""
        self.send_response(400)
        self.end_headers()

    def respond401(self):
        """401 Unauthorized"""
        self.send_response(401)
        self.end_headers()

    def respond404(self):
        """404 Not Found"""
        self.send_response(404)
        self.end_headers()
        #self.wfile.write(bytes("Not found.", "utf-8"))

    def respond409(self):
        """409 Conflict"""
        self.send_response(409)
        self.end_headers()


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--port",
        help="define port server listens on",
        type=int
    )
    args = parser.parse_args()

    listen = ("https://blooming-ocean-26004.herokuapp.com", args.port)
    server = HTTPServer(listen, MyRequestHandler)




    print("Listening on port {}...".format(args.port))
    server.serve_forever()


run()