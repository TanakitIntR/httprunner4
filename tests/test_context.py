import os
import unittest

from ate import utils, runner
from ate.context import Context
from ate.exception import ParamsError


class VariableBindsUnittest(unittest.TestCase):

    def setUp(self):
        self.context = Context()
        testcase_file_path = os.path.join(os.getcwd(), 'tests/data/demo_binds.yml')
        self.testcases = utils.load_testcases(testcase_file_path)

    def test_context_init_functions(self):
        self.assertIn("get_timestamp", self.context.testset_functions_config)
        self.assertIn("gen_random_string", self.context.testset_functions_config)

        variable_binds = [
            {"random": "${gen_random_string(5)}"},
            {"timestamp10": "${get_timestamp(10)}"}
        ]
        self.context.bind_variables(variable_binds)
        context_variables = self.context.get_testcase_variables_mapping()

        self.assertEqual(len(context_variables["random"]), 5)
        self.assertEqual(len(context_variables["timestamp10"]), 10)

    def test_context_bind_testset_variables(self):
        # testcase in JSON format
        testcase1 = {
            "variable_binds": [
                {"GLOBAL_TOKEN": "debugtalk"},
                {"token": "$GLOBAL_TOKEN"}
            ]
        }
        # testcase in YAML format
        testcase2 = self.testcases["bind_variables"]

        for testcase in [testcase1, testcase2]:
            variable_binds = testcase['variable_binds']
            self.context.bind_variables(variable_binds, level="testset")

            testset_variables = self.context.testset_shared_variables_mapping
            testcase_variables = self.context.get_testcase_variables_mapping()
            self.assertIn("GLOBAL_TOKEN", testset_variables)
            self.assertIn("GLOBAL_TOKEN", testcase_variables)
            self.assertEqual(testset_variables["GLOBAL_TOKEN"], "debugtalk")
            self.assertIn("token", testset_variables)
            self.assertIn("token", testcase_variables)
            self.assertEqual(testset_variables["token"], "debugtalk")

    def test_context_bind_testcase_variables(self):
        testcase1 = {
            "variable_binds": [
                {"GLOBAL_TOKEN": "debugtalk"},
                {"token": "$GLOBAL_TOKEN"}
            ]
        }
        testcase2 = self.testcases["bind_variables"]

        for testcase in [testcase1, testcase2]:
            variable_binds = testcase['variable_binds']
            self.context.bind_variables(variable_binds)

            testset_variables = self.context.testset_shared_variables_mapping
            testcase_variables = self.context.get_testcase_variables_mapping()
            self.assertNotIn("GLOBAL_TOKEN", testset_variables)
            self.assertIn("GLOBAL_TOKEN", testcase_variables)
            self.assertEqual(testcase_variables["GLOBAL_TOKEN"], "debugtalk")
            self.assertNotIn("token", testset_variables)
            self.assertIn("token", testcase_variables)
            self.assertEqual(testcase_variables["token"], "debugtalk")

    def test_context_bind_lambda_functions(self):
        testcase1 = {
            "function_binds": {
                "add_one": lambda x: x + 1,
                "add_two_nums": lambda x, y: x + y
            },
            "variable_binds": [
                {"add1": "${add_one(2)}"},
                {"sum2nums": "${add_two_nums(2,3)}"}
            ]
        }
        testcase2 = self.testcases["bind_lambda_functions"]

        for testcase in [testcase1, testcase2]:
            function_binds = testcase.get('function_binds', {})
            self.context.bind_functions(function_binds)

            variable_binds = testcase['variable_binds']
            self.context.bind_variables(variable_binds)

            context_variables = self.context.get_testcase_variables_mapping()
            self.assertIn("add1", context_variables)
            self.assertEqual(context_variables["add1"], 3)
            self.assertIn("sum2nums", context_variables)
            self.assertEqual(context_variables["sum2nums"], 5)

    def test_context_bind_lambda_functions_with_import(self):
        testcase1 = {
            "requires": ["random", "string", "hashlib"],
            "function_binds": {
                "gen_random_string": "lambda str_len: ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(str_len))",
                "gen_md5": "lambda *str_args: hashlib.md5(''.join(str_args).encode('utf-8')).hexdigest()"
            },
            "variable_binds": [
                {"TOKEN": "debugtalk"},
                {"random": "${gen_random_string(5)}"},
                {"data": '{"name": "user", "password": "123456"}'},
                {"authorization": "${gen_md5($TOKEN, $data, $random)}"}
            ]
        }
        testcase2 = self.testcases["bind_lambda_functions_with_import"]

        for testcase in [testcase1, testcase2]:
            requires = testcase.get('requires', [])
            self.context.import_requires(requires)

            function_binds = testcase.get('function_binds', {})
            self.context.bind_functions(function_binds)

            variable_binds = testcase['variable_binds']
            self.context.bind_variables(variable_binds)
            context_variables = self.context.get_testcase_variables_mapping()

            self.assertIn("TOKEN", context_variables)
            TOKEN = context_variables["TOKEN"]
            self.assertEqual(TOKEN, "debugtalk")
            self.assertIn("random", context_variables)
            self.assertIsInstance(context_variables["random"], str)
            self.assertEqual(len(context_variables["random"]), 5)
            random = context_variables["random"]
            self.assertIn("data", context_variables)
            data = context_variables["data"]
            self.assertIn("authorization", context_variables)
            self.assertEqual(len(context_variables["authorization"]), 32)
            authorization = context_variables["authorization"]
            self.assertEqual(utils.gen_md5(TOKEN, data, random), authorization)

    def test_import_module_functions(self):
        testcase1 = {
            "import_module_functions": ["tests.data.debugtalk"],
            "variable_binds": [
                {"TOKEN": "debugtalk"},
                {"random": "${gen_random_string(5)}"},
                {"data": '{"name": "user", "password": "123456"}'},
                {"authorization": "${gen_md5($TOKEN, $data, $random)}"}
            ]
        }
        testcase2 = self.testcases["bind_module_functions"]

        for testcase in [testcase1, testcase2]:
            module_functions = testcase.get('import_module_functions', [])
            self.context.import_module_functions(module_functions)

            variable_binds = testcase['variable_binds']
            self.context.bind_variables(variable_binds)
            context_variables = self.context.get_testcase_variables_mapping()

            self.assertIn("TOKEN", context_variables)
            TOKEN = context_variables["TOKEN"]
            self.assertEqual(TOKEN, "debugtalk")
            self.assertIn("random", context_variables)
            self.assertIsInstance(context_variables["random"], str)
            self.assertEqual(len(context_variables["random"]), 5)
            random = context_variables["random"]
            self.assertIn("data", context_variables)
            data = context_variables["data"]
            self.assertIn("authorization", context_variables)
            self.assertEqual(len(context_variables["authorization"]), 32)
            authorization = context_variables["authorization"]
            self.assertEqual(utils.gen_md5(TOKEN, data, random), authorization)

    def test_register_request(self):
        request_dict = {
            "url": "http://debugtalk.com",
            "method": "GET",
            "headers": {
                "Content-Type": "application/json",
                "USER-AGENT": "ios/10.3"
            }
        }
        self.context.register_request(request_dict)

        parsed_request = self.context.get_parsed_request()
        self.assertIn("content-type", parsed_request["headers"])
        self.assertIn("user-agent", parsed_request["headers"])

        request_dict = {
            "headers": "invalid headers"
        }
        with self.assertRaises(ParamsError):
            self.context.register_request(request_dict)


    def test_get_parsed_request(self):
        test_runner = runner.Runner()
        testcase = {
            "import_module_functions": ["tests.data.debugtalk"],
            "variable_binds": [
                {"TOKEN": "debugtalk"},
                {"random": "${gen_random_string(5)}"},
                {"data": '{"name": "user", "password": "123456"}'},
                {"authorization": "${gen_md5($TOKEN, $data, $random)}"}
            ],
            "request": {
                "url": "http://127.0.0.1:5000/api/users/1000",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json",
                    "authorization": "$authorization",
                    "random": "$random"
                },
                "data": "$data"
            }
        }
        test_runner.init_config(testcase, level="testcase")
        parsed_request = test_runner.context.get_parsed_request()
        self.assertIn("authorization", parsed_request["headers"])
        self.assertEqual(len(parsed_request["headers"]["authorization"]), 32)
        self.assertIn("random", parsed_request["headers"])
        self.assertEqual(len(parsed_request["headers"]["random"]), 5)
        self.assertIn("data", parsed_request)
        self.assertEqual(parsed_request["data"], testcase["variable_binds"][2]["data"])
