# NOTICE: Generated By HttpRunner. DO'NOT EDIT!
import unittest

from httprunner.runner import TestCaseRunner
from httprunner.schema import TestsConfig, TestStep


class TestCaseHardcode(unittest.TestCase):
    config = TestsConfig(
        **{
            "name": "request methods testcase in hardcode",
            "base_url": "https://postman-echo.com",
            "verify": False,
            "path": "examples/postman_echo/request_methods/hardcode_test.py",
        }
    )

    teststeps = [
        TestStep(
            **{
                "name": "get with params",
                "request": {
                    "method": "GET",
                    "url": "/get",
                    "params": {"foo1": "bar1", "foo2": "bar2"},
                    "headers": {"User-Agent": "HttpRunner/3.0"},
                },
                "validate": [{"eq": ["status_code", 200]}],
            }
        ),
        TestStep(
            **{
                "name": "post raw text",
                "request": {
                    "method": "POST",
                    "url": "/post",
                    "headers": {
                        "User-Agent": "HttpRunner/3.0",
                        "Content-Type": "text/plain",
                    },
                    "data": "This is expected to be sent back as part of response body.",
                },
                "validate": [{"eq": ["status_code", 200]}],
            }
        ),
        TestStep(
            **{
                "name": "post form data",
                "request": {
                    "method": "POST",
                    "url": "/post",
                    "headers": {
                        "User-Agent": "HttpRunner/3.0",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    "data": "foo1=bar1&foo2=bar2",
                },
                "validate": [{"eq": ["status_code", 200]}],
            }
        ),
        TestStep(
            **{
                "name": "put request",
                "request": {
                    "method": "PUT",
                    "url": "/put",
                    "headers": {
                        "User-Agent": "HttpRunner/3.0",
                        "Content-Type": "text/plain",
                    },
                    "data": "This is expected to be sent back as part of response body.",
                },
                "validate": [{"eq": ["status_code", 200]}],
            }
        ),
    ]

    def test_start(self):
        TestCaseRunner(self.config, self.teststeps).run()
