from os import urandom, environ

# heroku port
PORT = int(environ.get("PORT", 5000))

SECRET_KEY = urandom(32)
