import os

import requests
from ate import exception, runner, testcase, utils

from tests.base import ApiServerUnittest


class TestRunner(ApiServerUnittest):

    def setUp(self):
        self.test_runner = runner.Runner()
        self.reset_all()

        self.testcase_file_path_list = [
            os.path.join(
                os.getcwd(), 'tests/data/demo_testset_hardcode.yml'),
            os.path.join(
                os.getcwd(), 'tests/data/demo_testset_hardcode.json')
        ]

    def reset_all(self):
        url = "%s/api/reset-all" % self.host
        headers = self.get_authenticated_headers()
        return self.api_client.get(url, headers=headers)

    def test_run_single_testcase(self):
        for testcase_file_path in self.testcase_file_path_list:
            testcases = utils.load_tests(testcase_file_path)
            testcase = testcases[0]["test"]
            self.assertTrue(self.test_runner._run_test(testcase))

            testcase = testcases[1]["test"]
            self.assertTrue(self.test_runner._run_test(testcase))

            testcase = testcases[2]["test"]
            self.assertTrue(self.test_runner._run_test(testcase))

    def test_run_single_testcase_fail(self):
        testcase = {
            "name": "get token",
            "request": {
                "url": "http://127.0.0.1:5000/api/get-token",
                "method": "POST",
                "headers": {
                    "content-type": "application/json",
                    "user_agent": "iOS/10.3",
                    "device_sn": "HZfFBh6tU59EdXJ",
                    "os_platform": "ios",
                    "app_version": "2.8.6"
                },
                "json": {
                    "sign": "f1219719911caae89ccc301679857ebfda115ca2"
                }
            },
            "extract": [
                {"token": "content.token"}
            ],
            "validate": [
                {"check": "status_code", "comparator": "eq", "expected": 205},
                {"check": "content.token", "comparator": "len_eq", "expected": 19}
            ]
        }

        with self.assertRaises(exception.ValidationError):
            self.test_runner._run_test(testcase)

    def test_run_testset_hardcode(self):
        for testcase_file_path in self.testcase_file_path_list:
            result = self.test_runner.run(testcase_file_path)
            self.assertTrue(result["success"])

    def test_run_testsets_hardcode(self):
        for testcase_file_path in self.testcase_file_path_list:
            result = self.test_runner.run(testcase_file_path)
            self.assertTrue(result["success"])

    def test_run_testset_template_variables(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_variables.yml')
        result = self.test_runner.run(testcase_file_path)
        self.assertTrue(result["success"])

    def test_run_testset_template_import_functions(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_template_import_functions.yml')
        result = self.test_runner.run(testcase_file_path)
        self.assertTrue(result["success"])

    def test_run_testsets_template_import_functions(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_template_import_functions.yml')
        result = self.test_runner.run(testcase_file_path)
        self.assertTrue(result["success"])

    def test_run_testsets_template_lambda_functions(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_template_lambda_functions.yml')
        result = self.test_runner.run(testcase_file_path)
        self.assertTrue(result["success"])

    def test_run_testset_layered(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_layer.yml')
        result = self.test_runner.run(testcase_file_path)
        self.assertTrue(result["success"])

    def test_run_testset_output(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_layer.yml')
        result = self.test_runner.run(testcase_file_path)
        self.assertTrue(result["success"])
        self.assertIn("token", result["output"])

    def test_run_testset_with_variables_mapping(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_layer.yml')
        variables_mapping = {
            "app_version": '2.9.7'
        }
        result = self.test_runner.run(testcase_file_path, variables_mapping)
        self.assertTrue(result["success"])
        self.assertIn("token", result["output"])
