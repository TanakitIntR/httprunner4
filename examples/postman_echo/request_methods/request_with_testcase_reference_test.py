# NOTICE: Generated By HttpRunner. DO'NOT EDIT!
import unittest

from httprunner.runner import HttpRunner
from httprunner.schema import TConfig, TStep


class TestCaseRequestWithTestcaseReference(unittest.TestCase):
    config = TConfig(
        **{
            "name": "request methods testcase: reference testcase",
            "variables": {"foo1": "session_bar1"},
            "base_url": "https://postman-echo.com",
            "verify": False,
            "path": "examples/postman_echo/request_methods/request_with_testcase_reference_test.py",
        }
    )

    teststeps = [
        TStep(
            **{
                "name": "request with variables",
                "variables": {"foo1": "override_bar1"},
                "testcase": "request_methods/request_with_variables.yml",
            }
        ),
    ]

    def test_start(self):
        HttpRunner(self.config, self.teststeps).run()
