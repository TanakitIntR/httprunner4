# NOTICE: Generated By HttpRunner. DO'NOT EDIT!
import unittest

from httprunner.runner import TestCaseRunner
from httprunner.schema import TestsConfig, TestStep


class TestCaseValidateWithFunctions(unittest.TestCase):
    config = TestsConfig(
        **{
            "name": "request methods testcase: validate with functions",
            "variables": {"foo1": "session_bar1"},
            "base_url": "https://postman-echo.com",
            "verify": False,
            "path": "examples/postman_echo/request_methods/validate_with_functions_test.py",
        }
    )

    teststeps = [
        TestStep(
            **{
                "name": "get with params",
                "variables": {
                    "foo1": "bar1",
                    "foo2": "session_bar2",
                    "sum_v": "${sum_two(1, 2)}",
                },
                "request": {
                    "method": "GET",
                    "url": "/get",
                    "params": {"foo1": "$foo1", "foo2": "$foo2", "sum_v": "$sum_v"},
                    "headers": {"User-Agent": "HttpRunner/${get_httprunner_version()}"},
                },
                "extract": {"session_foo2": "body.args.foo2"},
                "validate": [
                    {"eq": ["status_code", 200]},
                    {"eq": ["body.args.sum_v", 3]},
                    {"less_than": ["body.args.sum_v", "${sum_two(2, 2)}"]},
                ],
            }
        ),
    ]

    def test_start(self):
        TestCaseRunner(self.config, self.teststeps).run()
