# encoding: utf-8

"""
Built-in dependent functions used in YAML/JSON testcases.
"""

import datetime
import json
import random
import re
import string
import time

from httprunner.compat import basestring, builtin_str, integer_types, str
from httprunner.exception import ParamsError


def gen_random_string(str_len):
    """ generate random string with specified length
    """
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(str_len))

def get_timestamp(str_len=13):
    """ get timestamp string, length can only between 0 and 16
    """
    if isinstance(str_len, integer_types) and 0 < str_len < 17:
        return builtin_str(time.time()).replace(".", "")[:str_len]

    raise ParamsError("timestamp length can only between 0 and 16.")

def get_current_date(fmt="%Y-%m-%d"):
    """ get current date, default format is %Y-%m-%d
    """
    return datetime.datetime.now().strftime(fmt)


""" built-in comparators
"""
def equals(check_value, expect_value):
    assert check_value == expect_value

def less_than(check_value, expect_value):
    assert check_value < expect_value

def less_than_or_equals(check_value, expect_value):
    assert check_value <= expect_value

def greater_than(check_value, expect_value):
    assert check_value > expect_value

def greater_than_or_equals(check_value, expect_value):
    assert check_value >= expect_value

def not_equals(check_value, expect_value):
    assert check_value != expect_value

def string_equals(check_value, expect_value):
    assert builtin_str(check_value) == builtin_str(expect_value)

def length_equals(check_value, expect_value):
    assert isinstance(expect_value, integer_types)
    assert len(check_value) == expect_value

def length_greater_than(check_value, expect_value):
    assert isinstance(expect_value, integer_types)
    assert len(check_value) > expect_value

def length_greater_than_or_equals(check_value, expect_value):
    assert isinstance(expect_value, integer_types)
    assert len(check_value) >= expect_value

def length_less_than(check_value, expect_value):
    assert isinstance(expect_value, integer_types)
    assert len(check_value) < expect_value

def length_less_than_or_equals(check_value, expect_value):
    assert isinstance(expect_value, integer_types)
    assert len(check_value) <= expect_value

def contains(check_value, expect_value):
    assert isinstance(check_value, (list, tuple, dict, basestring))
    assert expect_value in check_value

def contained_by(check_value, expect_value):
    assert isinstance(expect_value, (list, tuple, dict, basestring))
    assert check_value in expect_value

def type_match(check_value, expect_value):
    def get_type(name):
        if isinstance(name, type):
            return name
        elif isinstance(name, basestring):
            try:
                return __builtins__[name]
            except KeyError:
                raise ValueError(name)
        else:
            raise ValueError(name)

    assert isinstance(check_value, get_type(expect_value))

def regex_match(check_value, expect_value):
    assert isinstance(expect_value, basestring)
    assert isinstance(check_value, basestring)
    assert re.match(expect_value, check_value)

def startswith(check_value, expect_value):
    assert builtin_str(check_value).startswith(builtin_str(expect_value))

def endswith(check_value, expect_value):
    assert builtin_str(check_value).endswith(builtin_str(expect_value))

""" built-in hooks
"""
def setup_hook_prepare_kwargs(method, url, kwargs):
    if method == "POST":
        content_type = kwargs.get("headers", {}).get("content-type")
        if content_type and "data" in kwargs:
            # if request content-type is application/json, request data should be dumped
            if content_type.startswith("application/json"):
                kwargs["data"] = json.dumps(kwargs["data"])

            if isinstance(kwargs["data"], str):
                kwargs["data"] = kwargs["data"].encode('utf-8')

def setup_hook_httpntlmauth(method, url, kwargs):
    if "httpntlmauth" in kwargs:
        from requests_ntlm import HttpNtlmAuth
        auth_account = kwargs.pop("httpntlmauth")
        kwargs["auth"] = HttpNtlmAuth(
            auth_account["username"], auth_account["password"])

def teardown_hook_sleep_1_secs(resp_obj):
    """ sleep 1 seconds after request
    """
    time.sleep(1)
