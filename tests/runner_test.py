import unittest

from httprunner import loader
from httprunner.runner import HttpRunner


class TestHttpRunner(unittest.TestCase):
    def setUp(self):
        loader.project_meta = None
        self.runner = HttpRunner()

    def test_run_testcase_by_path_request_only(self):
        self.runner.run_path(
            "examples/postman-echo/request.methods/request_with_functions.yml"
        )
        result = self.runner.get_summary()
        self.assertTrue(result.success)
        self.assertEqual(result.name, "request methods testcase with functions")
        self.assertEqual(result.step_datas[0].name, "get with params")
        self.assertEqual(len(result.step_datas), 3)

    def test_run_testcase_by_path_ref_testcase(self):
        self.runner.run_path(
            "examples/postman-echo/request.methods/request_with_testcase_reference.yml"
        )
        result = self.runner.get_summary()
        self.assertTrue(result.success)
        self.assertEqual(result.name, "request methods testcase: reference testcase")
        self.assertEqual(result.step_datas[0].name, "request with functions")
        self.assertEqual(len(result.step_datas), 2)
