import hashlib
import hmac
import json
import random
import string
import time

try:
    string_type = basestring
    PYTHON_VERSION = 2
    import urllib
except NameError:
    string_type = str
    PYTHON_VERSION = 3
    import urllib.parse as urllib

SECRET_KEY = "DebugTalk"

def get_sign(*args):
    content = ''.join(args).encode('ascii')
    sign_key = SECRET_KEY.encode('ascii')
    sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
    return sign

get_sign_lambda = lambda *args: hmac.new(
    'DebugTalk'.encode('ascii'),
    ''.join(args).encode('ascii'),
    hashlib.sha1).hexdigest()

def gen_md5(*args):
    return hashlib.md5("".join(args).encode('utf-8')).hexdigest()
