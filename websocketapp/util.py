import json
import itsdangerous
from flask.sessions import SecureCookieSessionInterface
import os

class MockApp(object):
    def __init__(self, secret_key):
        self.secret_key = secret_key

def decode_cookie(cookie, secret_key=os.environ.get("SECRET_KEY")):
    app = MockApp(secret_key)
    si = SecureCookieSessionInterface()
    s = si.get_signing_serializer(app)
    try:
        res = s.loads(cookie)
        return res
    except itsdangerous.exc.BadTimeSignature:
        return "invalid"

