import os
import shutil
import time

from httprunner import HttpRunner, api, loader, parser
from locust import HttpLocust
from tests.api_server import HTTPBIN_SERVER
from tests.base import ApiServerUnittest


class TestHttpRunner(ApiServerUnittest):

    def setUp(self):
        self.testcase_cli_path = "tests/data/demo_testcase_cli.yml"
        self.testcase_file_path_list = [
            os.path.join(
                os.getcwd(), 'tests/data/demo_testcase_hardcode.yml'),
            os.path.join(
                os.getcwd(), 'tests/data/demo_testcase_hardcode.json')
        ]
        testcases = [{
            'config': {
                'name': 'testcase description',
                'request': {
                    'base_url': '',
                    'headers': {'User-Agent': 'python-requests/2.18.4'}
                },
                'variables': []
            },
            'teststeps': [
                {
                    'name': '/api/get-token',
                    'request': {
                        'url': 'http://127.0.0.1:5000/api/get-token',
                        'method': 'POST',
                        'headers': {'Content-Type': 'application/json', 'app_version': '2.8.6', 'device_sn': 'FwgRiO7CNA50DSU', 'os_platform': 'ios', 'user_agent': 'iOS/10.3'},
                        'json': {'sign': '958a05393efef0ac7c0fb80a7eac45e24fd40c27'}
                    },
                    'extract': [
                        {'token': 'content.token'}
                    ],
                    'validate': [
                        {'eq': ['status_code', 200]},
                        {'eq': ['headers.Content-Type', 'application/json']},
                        {'eq': ['content.success', True]}
                    ]
                },
                {
                    'name': '/api/users/1000',
                    'request': {
                        'url': 'http://127.0.0.1:5000/api/users/1000',
                        'method': 'POST',
                        'headers': {'Content-Type': 'application/json', 'device_sn': 'FwgRiO7CNA50DSU','token': '$token'}, 'json': {'name': 'user1', 'password': '123456'}
                    },
                    'validate': [
                        {'eq': ['status_code', 201]},
                        {'eq': ['headers.Content-Type', 'application/json']},
                        {'eq': ['content.success', True]},
                        {'eq': ['content.msg', 'user created successfully.']}
                    ]
                }
            ]
        }]
        self.tests_mapping = {
            "testcases": testcases
        }
        self.reset_all()

    def reset_all(self):
        url = "%s/api/reset-all" % self.host
        headers = self.get_authenticated_headers()
        return self.api_client.get(url, headers=headers)

    def test_text_run_times(self):
        runner = HttpRunner().run(self.testcase_cli_path)
        self.assertEqual(runner.summary["stat"]["testsRun"], 10)

    def test_text_skip(self):
        runner = HttpRunner().run(self.testcase_cli_path)
        self.assertEqual(runner.summary["stat"]["skipped"], 4)

    def test_html_report(self):
        runner = HttpRunner().run(self.testcase_cli_path)
        summary = runner.summary
        self.assertEqual(summary["stat"]["testsRun"], 10)
        self.assertEqual(summary["stat"]["skipped"], 4)

        output_folder_name = "demo"
        runner.gen_html_report(html_report_name=output_folder_name)
        report_save_dir = os.path.join(os.getcwd(), 'reports', output_folder_name)
        self.assertGreater(len(os.listdir(report_save_dir)), 0)
        shutil.rmtree(report_save_dir)

    def test_run_testcases(self):
        runner = HttpRunner().run(self.tests_mapping)
        summary = runner.summary
        self.assertTrue(summary["success"])
        self.assertEqual(summary["stat"]["testsRun"], 2)
        self.assertIn("details", summary)
        self.assertIn("records", summary["details"][0])

    def test_run_yaml_upload(self):
        runner = HttpRunner().run("tests/httpbin/upload.yml")
        summary = runner.summary
        self.assertTrue(summary["success"])
        self.assertEqual(summary["stat"]["testsRun"], 1)
        self.assertIn("details", summary)
        self.assertIn("records", summary["details"][0])

    def test_run_post_data(self):
        testcases = [
            {
                "config": {
                    'name': "post data",
                    'request': {
                        'base_url': '',
                        'headers': {'User-Agent': 'python-requests/2.18.4'}
                    },
                    'variables': []
                },
                "teststeps": [
                    {
                        "name": "post data",
                        "request": {
                            "url": "{}/post".format(HTTPBIN_SERVER),
                            "method": "POST",
                            "headers": {
                                "Content-Type": "application/json"
                            },
                            "data": "abc"
                        },
                        "validate": [
                            {"eq": ["status_code", 200]}
                        ]
                    }
                ]
            }
        ]
        tests_mapping = {
            "testcases": testcases
        }
        runner = HttpRunner().run(tests_mapping)
        summary = runner.summary
        self.assertTrue(summary["success"])
        self.assertEqual(summary["stat"]["testsRun"], 1)
        self.assertEqual(summary["details"][0]["records"][0]["meta_data"]["response"]["json"]["data"], "abc")

    def test_html_report_repsonse_image(self):
        runner = HttpRunner().run("tests/httpbin/load_image.yml")
        summary = runner.summary
        output_folder_name = "demo"
        report = runner.gen_html_report(html_report_name=output_folder_name)
        self.assertTrue(os.path.isfile(report))
        report_save_dir = os.path.join(os.getcwd(), 'reports', output_folder_name)
        shutil.rmtree(report_save_dir)

    def test_testcase_layer_with_api(self):
        runner = HttpRunner(failfast=True).run("tests/testcases/setup.yml")
        summary = runner.summary
        self.assertTrue(summary["success"])
        self.assertEqual(summary["details"][0]["records"][0]["name"], "get token (setup)")
        self.assertEqual(summary["stat"]["testsRun"], 2)

    def test_testcase_layer_with_testcase(self):
        runner = HttpRunner(failfast=True).run("tests/testsuites/create_users.yml")
        summary = runner.summary
        self.assertTrue(summary["success"])
        self.assertEqual(summary["stat"]["testsRun"], 2)

    def test_run_httprunner_with_hooks(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/httpbin/hooks.yml')
        start_time = time.time()
        runner = HttpRunner().run(testcase_file_path)
        end_time = time.time()
        summary = runner.summary
        self.assertTrue(summary["success"])
        self.assertLess(end_time - start_time, 60)

    def test_run_httprunner_with_teardown_hooks_alter_response(self):
        testcases = [
            {
                "config": {"name": "test teardown hooks"},
                "teststeps": [
                    {
                        "name": "test teardown hooks",
                        "request": {
                            "url": "{}/headers".format(HTTPBIN_SERVER),
                            "method": "GET",
                            "data": "abc"
                        },
                        "teardown_hooks": [
                            "${alter_response($response)}"
                        ],
                        "validate": [
                            {"eq": ["status_code", 500]},
                            {"eq": ["headers.content-type", "html/text"]},
                            {"eq": ["json.headers.Host", "127.0.0.1:8888"]},
                            {"eq": ["content.headers.Host", "127.0.0.1:8888"]},
                            {"eq": ["text.headers.Host", "127.0.0.1:8888"]},
                            {"eq": ["new_attribute", "new_attribute_value"]},
                            {"eq": ["new_attribute_dict", {"key": 123}]},
                            {"eq": ["new_attribute_dict.key", 123]}
                        ]
                    }
                ]
            }
        ]
        loader.load_project_tests("tests")
        tests_mapping = {
            "project_mapping": loader.project_mapping,
            "testcases": testcases
        }
        runner = HttpRunner().run(tests_mapping)
        summary = runner.summary
        self.assertTrue(summary["success"])

    def test_run_httprunner_with_teardown_hooks_not_exist_attribute(self):
        testcases = [
            {
                "config": {
                    "name": "test teardown hooks"
                },
                "teststeps": [
                    {
                        "name": "test teardown hooks",
                        "request": {
                            "url": "{}/headers".format(HTTPBIN_SERVER),
                            "method": "GET",
                            "data": "abc"
                        },
                        "teardown_hooks": [
                            "${alter_response($response)}"
                        ],
                        "validate": [
                            {"eq": ["attribute_not_exist", "new_attribute"]}
                        ]
                    }
                ]
            }
        ]
        loader.load_project_tests("tests")
        tests_mapping = {
            "project_mapping": loader.project_mapping,
            "testcases": testcases
        }
        runner = HttpRunner().run(tests_mapping)
        summary = runner.summary
        self.assertFalse(summary["success"])
        self.assertEqual(summary["stat"]["errors"], 1)

    def test_run_httprunner_with_teardown_hooks_error(self):
        testcases = [
            {
                "config": {
                    "name": "test teardown hooks"
                },
                "teststeps": [
                    {
                        "name": "test teardown hooks",
                        "request": {
                            "url": "{}/headers".format(HTTPBIN_SERVER),
                            "method": "GET",
                            "data": "abc"
                        },
                        "teardown_hooks": [
                            "${alter_response_error($response)}"
                        ]
                    }
                ]
            }
        ]
        loader.load_project_tests("tests")
        tests_mapping = {
            "project_mapping": loader.project_mapping,
            "testcases": testcases
        }
        runner = HttpRunner().run(tests_mapping)
        summary = runner.summary
        self.assertFalse(summary["success"])
        self.assertEqual(summary["stat"]["errors"], 1)

    def test_run_testcase_hardcode(self):
        for testcase_file_path in self.testcase_file_path_list:
            runner = HttpRunner().run(testcase_file_path)
            summary = runner.summary
            self.assertTrue(summary["success"])
            self.assertEqual(summary["stat"]["testsRun"], 3)
            self.assertEqual(summary["stat"]["successes"], 3)

    def test_run_testcase_template_variables(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testcase_variables.yml')
        runner = HttpRunner().run(testcase_file_path)
        summary = runner.summary
        self.assertTrue(summary["success"])

    def test_run_testcase_template_import_functions(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testcase_functions.yml')
        runner = HttpRunner().run(testcase_file_path)
        summary = runner.summary
        self.assertTrue(summary["success"])

    def test_run_testcase_layered(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testcase_layer.yml')
        runner = HttpRunner().run(testcase_file_path)
        summary = runner.summary
        self.assertTrue(summary["success"])
        self.assertEqual(len(summary["details"]), 1)

    def test_run_testcase_output(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testcase_layer.yml')
        runner = HttpRunner(failfast=True).run(testcase_file_path)
        summary = runner.summary
        self.assertTrue(summary["success"])
        self.assertIn("token", summary["details"][0]["in_out"]["out"])
        # TODO: add
        # self.assertIn("user_agent", summary["details"][0]["in_out"]["in"])

    def test_run_testcase_with_variables_mapping(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testcase_layer.yml')
        variables_mapping = {
            "app_version": '2.9.7'
        }
        runner = HttpRunner(failfast=True).run(testcase_file_path, mapping=variables_mapping)
        summary = runner.summary
        self.assertTrue(summary["success"])
        self.assertIn("token", summary["details"][0]["in_out"]["out"])
        # TODO: add
        # self.assertGreater(len(summary["details"][0]["in_out"]["in"]), 3)

    def test_run_testcase_with_parameters(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_parameters.yml')
        runner = HttpRunner().run(testcase_file_path)
        summary = runner.summary
        # TODO: add parameterize
        # self.assertEqual(
        #     summary["details"][0]["in_out"]["in"]["user_agent"],
        #     "iOS/10.1"
        # )
        # self.assertEqual(
        #     summary["details"][2]["in_out"]["in"]["user_agent"],
        #     "iOS/10.2"
        # )
        # self.assertEqual(
        #     summary["details"][4]["in_out"]["in"]["user_agent"],
        #     "iOS/10.3"
        # )
        self.assertTrue(summary["success"])
        self.assertEqual(len(summary["details"]), 1)
        # self.assertEqual(len(summary["details"]), 3 * 2)
        # self.assertEqual(summary["stat"]["testsRun"], 3 * 2)
        self.assertIn("in", summary["details"][0]["in_out"])
        self.assertIn("out", summary["details"][0]["in_out"])

    def test_run_testcase_with_parameters_name(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_parameters.yml')
        tests_mapping = loader.load_tests(testcase_file_path)
        parser.parse_tests(tests_mapping)
        runner = HttpRunner()
        test_suite = runner._add_tests(tests_mapping)

        self.assertEqual(
            test_suite._tests[0].teststeps[0]['name'],
            'get token with iOS/10.1 and test1'
        )
        # TODO: add parameterize
        # self.assertEqual(
        #     test_suite._tests[1].teststeps[0]['name'],
        #     'get token with iOS/10.1 and test2'
        # )
        # self.assertEqual(
        #     test_suite._tests[2].teststeps[0]['name'],
        #     'get token with iOS/10.2 and test1'
        # )
        # self.assertEqual(
        #     test_suite._tests[3].teststeps[0]['name'],
        #     'get token with iOS/10.2 and test2'
        # )
        # self.assertEqual(
        #     test_suite._tests[4].teststeps[0]['name'],
        #     'get token with iOS/10.3 and test1'
        # )
        # self.assertEqual(
        #     test_suite._tests[5].teststeps[0]['name'],
        #     'get token with iOS/10.3 and test2'
        # )

    def test_validate_response_content(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/httpbin/basic.yml')
        runner = HttpRunner().run(testcase_file_path)
        self.assertTrue(runner.summary["success"])


class TestApi(ApiServerUnittest):

    def test_testcase_loader(self):
        testcase_path = "tests/testcases/setup.yml"
        tests_mapping = loader.load_tests(testcase_path)

        project_mapping = tests_mapping["project_mapping"]
        self.assertIsInstance(project_mapping, dict)
        self.assertIn("PWD", project_mapping)
        self.assertIn("functions", project_mapping)
        self.assertIn("env", project_mapping)

        testcases = tests_mapping["testcases"]
        self.assertIsInstance(testcases, list)
        self.assertEqual(len(testcases), 1)
        testcase_config = testcases[0]["config"]
        self.assertEqual(testcase_config["name"], "setup and reset all.")
        self.assertIn("path", testcase_config)

        testcase_teststeps = testcases[0]["teststeps"]
        self.assertEqual(len(testcase_teststeps), 2)
        self.assertIn("api", testcase_teststeps[0])
        self.assertEqual(testcase_teststeps[0]["name"], "get token (setup)")
        self.assertIsInstance(testcase_teststeps[0]["variables"], list)
        self.assertIn("api_def", testcase_teststeps[0])
        self.assertEqual(testcase_teststeps[0]["api_def"]["request"]["url"], "/api/get-token")

    def test_testcase_parser(self):
        testcase_path = "tests/testcases/setup.yml"
        tests_mapping = loader.load_tests(testcase_path)

        parser.parse_tests(tests_mapping)
        parsed_testcases = tests_mapping["testcases"]

        self.assertEqual(len(parsed_testcases), 1)

        self.assertNotIn("variables", parsed_testcases[0]["config"])
        self.assertEqual(len(parsed_testcases[0]["teststeps"]), 2)

        teststep1 = parsed_testcases[0]["teststeps"][0]
        self.assertEqual(teststep1["name"], "get token (setup)")
        self.assertNotIn("api_def", teststep1)
        self.assertEqual(teststep1["variables"]["device_sn"], "TESTCASE_SETUP_XXX")
        self.assertEqual(teststep1["request"]["url"], "http://127.0.0.1:5000/api/get-token")

    def test_testcase_add_tests(self):
        testcase_path = "tests/testcases/setup.yml"
        tests_mapping = loader.load_tests(testcase_path)

        parser.parse_tests(tests_mapping)
        runner = HttpRunner()
        test_suite = runner._add_tests(tests_mapping)

        self.assertEqual(len(test_suite._tests), 1)
        teststeps = test_suite._tests[0].teststeps
        self.assertEqual(teststeps[0]["name"], "get token (setup)")
        self.assertEqual(teststeps[0]["variables"]["device_sn"], "TESTCASE_SETUP_XXX")
        self.assertIn("api", teststeps[0])

    def test_testcase_simple_run_suite(self):
        testcase_path = "tests/testcases/setup.yml"
        tests_mapping = loader.load_tests(testcase_path)
        parser.parse_tests(tests_mapping)
        runner = HttpRunner()
        test_suite = runner._add_tests(tests_mapping)
        tests_results = runner._run_suite(test_suite)
        self.assertEqual(len(tests_results[0][1].records), 2)

    def test_testcase_complex_run_suite(self):
        testcase_path = "tests/testcases/create_and_check.yml"
        tests_mapping = loader.load_tests(testcase_path)
        parser.parse_tests(tests_mapping)
        runner = HttpRunner()
        test_suite = runner._add_tests(tests_mapping)
        tests_results = runner._run_suite(test_suite)
        self.assertEqual(len(tests_results[0][1].records), 4)

        results = tests_results[0][1]
        self.assertEqual(
            results.records[0]["name"],
            "setup and reset all (override)."
        )
        self.assertEqual(
            results.records[1]["name"],
            "make sure user 9001 does not exist"
        )

    def test_testsuite_loader(self):
        testcase_path = "tests/testsuites/create_users.yml"
        tests_mapping = loader.load_tests(testcase_path)

        project_mapping = tests_mapping["project_mapping"]
        self.assertIsInstance(project_mapping, dict)
        self.assertIn("PWD", project_mapping)
        self.assertIn("functions", project_mapping)
        self.assertIn("env", project_mapping)

        testcases = tests_mapping["testcases"]
        self.assertIsInstance(testcases, list)
        self.assertEqual(len(testcases), 1)
        testcase_config = testcases[0]["config"]
        self.assertEqual(testcase_config["name"], "create users with uid")
        self.assertIn("path", testcase_config)

        testcase_teststeps = testcases[0]["teststeps"]
        self.assertEqual(len(testcase_teststeps), 2)
        self.assertIn("testcase_def", testcase_teststeps[0])
        self.assertEqual(testcase_teststeps[0]["name"], "create user 1000 and check result.")
        self.assertIsInstance(testcase_teststeps[0]["testcase_def"], dict)
        self.assertEqual(testcase_teststeps[0]["testcase_def"]["config"]["name"], "create user and check result.")
        self.assertEqual(len(testcase_teststeps[0]["testcase_def"]["teststeps"]), 4)
        self.assertEqual(testcase_teststeps[0]["testcase_def"]["teststeps"][0]["name"], "setup and reset all (override).")

    def test_testsuite_parser(self):
        testcase_path = "tests/testsuites/create_users.yml"
        tests_mapping = loader.load_tests(testcase_path)

        parser.parse_tests(tests_mapping)

        parsed_testcases = tests_mapping["testcases"]
        self.assertEqual(len(parsed_testcases), 1)
        self.assertEqual(len(parsed_testcases[0]["teststeps"]), 2)

        testcase1 = parsed_testcases[0]["teststeps"][0]
        self.assertEqual(testcase1["config"]["name"], "create user 1000 and check result.")
        self.assertNotIn("testcase_def", testcase1)
        self.assertEqual(len(testcase1["teststeps"]), 4)
        self.assertEqual(
            testcase1["teststeps"][0]["teststeps"][0]["request"]["url"],
            "http://127.0.0.1:5000/api/get-token"
        )
        self.assertEqual(len(testcase1["teststeps"][0]["teststeps"][0]["variables"]["device_sn"]), 15)

    def test_testsuite_add_tests(self):
        testcase_path = "tests/testsuites/create_users.yml"
        tests_mapping = loader.load_tests(testcase_path)

        parser.parse_tests(tests_mapping)
        runner = HttpRunner()
        test_suite = runner._add_tests(tests_mapping)

        self.assertEqual(len(test_suite._tests), 1)
        teststeps = test_suite._tests[0].teststeps
        self.assertEqual(teststeps[0]["config"]["name"], "create user 1000 and check result.")

    def test_testsuite_run_suite(self):
        testcase_path = "tests/testsuites/create_users.yml"
        tests_mapping = loader.load_tests(testcase_path)

        parser.parse_tests(tests_mapping)

        runner = HttpRunner()
        test_suite = runner._add_tests(tests_mapping)
        tests_results = runner._run_suite(test_suite)

        self.assertEqual(len(tests_results[0][1].records), 2)

        results = tests_results[0][1]
        self.assertEqual(
            results.records[0]["name"],
            "create user 1000 and check result."
        )
        self.assertEqual(
            results.records[1]["name"],
            "create user 1001 and check result."
        )