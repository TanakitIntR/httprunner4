import os
import time
import unittest

from ate import testcase
from ate.exception import ParamsError, ApiNotFound


class TestcaseParserUnittest(unittest.TestCase):

    def test_extract_variables(self):
        self.assertEqual(
            testcase.extract_variables("$var"),
            ["var"]
        )
        self.assertEqual(
            testcase.extract_variables("$var123"),
            ["var123"]
        )
        self.assertEqual(
            testcase.extract_variables("$var_name"),
            ["var_name"]
        )
        self.assertEqual(
            testcase.extract_variables("var"),
            []
        )
        self.assertEqual(
            testcase.extract_variables("a$var"),
            ["var"]
        )
        self.assertEqual(
            testcase.extract_variables("$v ar"),
            ["v"]
        )
        self.assertEqual(
            testcase.extract_variables(" "),
            []
        )
        self.assertEqual(
            testcase.extract_variables("$abc*"),
            ["abc"]
        )
        self.assertEqual(
            testcase.extract_variables("${func()}"),
            []
        )
        self.assertEqual(
            testcase.extract_variables("${func(1,2)}"),
            []
        )
        self.assertEqual(
            testcase.extract_variables("${gen_md5($TOKEN, $data, $random)}"),
            ["TOKEN", "data", "random"]
        )

    def test_eval_content_variables(self):
        variables = {
            "var_1": "abc",
            "var_2": "def",
            "var_3": 123,
            "var_4": {"a": 1},
            "var_5": True,
            "var_6": None
        }
        testcase_parser = testcase.TestcaseParser(variables=variables)
        self.assertEqual(
            testcase_parser.eval_content_variables("$var_1"),
            "abc"
        )
        self.assertEqual(
            testcase_parser.eval_content_variables("var_1"),
            "var_1"
        )
        self.assertEqual(
            testcase_parser.eval_content_variables("$var_1#XYZ"),
            "abc#XYZ"
        )
        self.assertEqual(
            testcase_parser.eval_content_variables("/$var_1/$var_2/var3"),
            "/abc/def/var3"
        )
        self.assertEqual(
            testcase_parser.eval_content_variables("/$var_1/$var_2/$var_1"),
            "/abc/def/abc"
        )
        self.assertEqual(
            testcase_parser.eval_content_variables("${func($var_1, $var_2, xyz)}"),
            "${func(abc, def, xyz)}"
        )
        self.assertEqual(
            testcase_parser.eval_content_variables("$var_3"),
            123
        )
        self.assertEqual(
            testcase_parser.eval_content_variables("$var_4"),
            {"a": 1}
        )
        self.assertEqual(
            testcase_parser.eval_content_variables("$var_5"),
            True
        )
        self.assertEqual(
            testcase_parser.eval_content_variables("abc$var_5"),
            "abcTrue"
        )
        self.assertEqual(
            testcase_parser.eval_content_variables("abc$var_4"),
            "abc{'a': 1}"
        )
        self.assertEqual(
            testcase_parser.eval_content_variables("$var_6"),
            None
        )

    def test_eval_content_variables_search_upward(self):
        testcase_parser = testcase.TestcaseParser()

        with self.assertRaises(ParamsError):
            testcase_parser.eval_content_variables("/api/$SECRET_KEY")

        testcase_parser.file_path = "tests/data/demo_testset_hardcode.yml"
        content = testcase_parser.eval_content_variables("/api/$SECRET_KEY")
        self.assertEqual(content, "/api/DebugTalk")

    def test_parse_string_value(self):
        self.assertEqual(testcase.parse_string_value("123"), 123)
        self.assertEqual(testcase.parse_string_value("12.3"), 12.3)
        self.assertEqual(testcase.parse_string_value("a123"), "a123")
        self.assertEqual(testcase.parse_string_value("$var"), "$var")
        self.assertEqual(testcase.parse_string_value("${func}"), "${func}")

    def test_parse_function(self):
        self.assertEqual(
            testcase.parse_function("func()"),
            {'func_name': 'func', 'args': [], 'kwargs': {}}
        )
        self.assertEqual(
            testcase.parse_function("func(5)"),
            {'func_name': 'func', 'args': [5], 'kwargs': {}}
        )
        self.assertEqual(
            testcase.parse_function("func(1, 2)"),
            {'func_name': 'func', 'args': [1, 2], 'kwargs': {}}
        )
        self.assertEqual(
            testcase.parse_function("func(a=1, b=2)"),
            {'func_name': 'func', 'args': [], 'kwargs': {'a': 1, 'b': 2}}
        )
        self.assertEqual(
            testcase.parse_function("func(a= 1, b =2)"),
            {'func_name': 'func', 'args': [], 'kwargs': {'a': 1, 'b': 2}}
        )
        self.assertEqual(
            testcase.parse_function("func(1, 2, a=3, b=4)"),
            {'func_name': 'func', 'args': [1, 2], 'kwargs': {'a': 3, 'b': 4}}
        )

    def test_parse_content_with_bindings_variables(self):
        variables = {
            "str_1": "str_value1",
            "str_2": "str_value2"
        }
        testcase_parser = testcase.TestcaseParser(variables=variables)
        self.assertEqual(
            testcase_parser.parse_content_with_bindings("$str_1"),
            "str_value1"
        )
        self.assertEqual(
            testcase_parser.parse_content_with_bindings("123$str_1/456"),
            "123str_value1/456"
        )

        with self.assertRaises(ParamsError):
            testcase_parser.parse_content_with_bindings("$str_3")

        self.assertEqual(
            testcase_parser.parse_content_with_bindings(["$str_1", "str3"]),
            ["str_value1", "str3"]
        )
        self.assertEqual(
            testcase_parser.parse_content_with_bindings({"key": "$str_1"}),
            {"key": "str_value1"}
        )

    def test_parse_content_with_bindings_multiple_identical_variables(self):
        variables = {
            "userid": 100,
            "data": 1498
        }
        testcase_parser = testcase.TestcaseParser(variables=variables)
        content = "/users/$userid/training/$data?userId=$userid&data=$data"
        self.assertEqual(
            testcase_parser.parse_content_with_bindings(content),
            "/users/100/training/1498?userId=100&data=1498"
        )

    def test_parse_variables_multiple_identical_variables(self):
        variables = {
            "user": 100,
            "userid": 1000,
            "data": 1498
        }
        testcase_parser = testcase.TestcaseParser(variables=variables)
        content = "/users/$user/$userid/$data?userId=$userid&data=$data"
        self.assertEqual(
            testcase_parser.parse_content_with_bindings(content),
            "/users/100/1000/1498?userId=1000&data=1498"
        )

    def test_parse_content_with_bindings_functions(self):
        import random, string
        functions = {
            "gen_random_string": lambda str_len: ''.join(random.choice(string.ascii_letters + string.digits) \
                for _ in range(str_len))
        }
        testcase_parser = testcase.TestcaseParser(functions=functions)

        result = testcase_parser.parse_content_with_bindings("${gen_random_string(5)}")
        self.assertEqual(len(result), 5)

        add_two_nums = lambda a, b=1: a + b
        functions["add_two_nums"] = add_two_nums
        self.assertEqual(
            testcase_parser.parse_content_with_bindings("${add_two_nums(1)}"),
            2
        )
        self.assertEqual(
            testcase_parser.parse_content_with_bindings("${add_two_nums(1, 2)}"),
            3
        )

    def test_extract_functions(self):
        self.assertEqual(
            testcase.extract_functions("${func()}"),
            ["func()"]
        )
        self.assertEqual(
            testcase.extract_functions("${func(5)}"),
            ["func(5)"]
        )
        self.assertEqual(
            testcase.extract_functions("${func(a=1, b=2)}"),
            ["func(a=1, b=2)"]
        )
        self.assertEqual(
            testcase.extract_functions("${func(1, $b, c=$x, d=4)}"),
            ["func(1, $b, c=$x, d=4)"]
        )
        self.assertEqual(
            testcase.extract_functions("/api/1000?_t=${get_timestamp()}"),
            ["get_timestamp()"]
        )
        self.assertEqual(
            testcase.extract_functions("/api/${add(1, 2)}"),
            ["add(1, 2)"]
        )
        self.assertEqual(
            testcase.extract_functions("/api/${add(1, 2)}?_t=${get_timestamp()}"),
            ["add(1, 2)", "get_timestamp()"]
        )
        self.assertEqual(
            testcase.extract_functions("abc${func(1, 2, a=3, b=4)}def"),
            ["func(1, 2, a=3, b=4)"]
        )

    def test_eval_content_functions(self):
        functions = {
            "add_two_nums": lambda a, b=1: a + b
        }
        testcase_parser = testcase.TestcaseParser(functions=functions)
        self.assertEqual(
            testcase_parser.eval_content_functions("${add_two_nums(1, 2)}"),
            3
        )
        self.assertEqual(
            testcase_parser.eval_content_functions("/api/${add_two_nums(1, 2)}"),
            "/api/3"
        )

    def test_eval_content_functions_search_upward(self):
        testcase_parser = testcase.TestcaseParser()

        with self.assertRaises(ParamsError):
            testcase_parser.eval_content_functions("/api/${gen_md5(abc)}")

        testcase_parser.file_path = "tests/data/demo_testset_hardcode.yml"
        content = testcase_parser.eval_content_functions("/api/${gen_md5(abc)}")
        self.assertEqual(content, "/api/900150983cd24fb0d6963f7d28e17f72")

    def test_parse_content_with_bindings_testcase(self):
        variables = {
            "uid": "1000",
            "random": "A2dEx",
            "authorization": "a83de0ff8d2e896dbd8efb81ba14e17d",
            "data": {"name": "user", "password": "123456"}
        }
        functions = {
            "add_two_nums": lambda a, b=1: a + b,
            "get_timestamp": lambda: int(time.time() * 1000)
        }
        testcase_template = {
            "url": "http://127.0.0.1:5000/api/users/$uid/${add_two_nums(1,2)}",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "authorization": "$authorization",
                "random": "$random",
                "sum": "${add_two_nums(1, 2)}"
            },
            "body": "$data"
        }
        parsed_testcase = testcase.TestcaseParser(variables, functions)\
            .parse_content_with_bindings(testcase_template)

        self.assertEqual(
            parsed_testcase["url"],
            "http://127.0.0.1:5000/api/users/1000/3"
        )
        self.assertEqual(
            parsed_testcase["headers"]["authorization"],
            variables["authorization"]
        )
        self.assertEqual(
            parsed_testcase["headers"]["random"],
            variables["random"]
        )
        self.assertEqual(
            parsed_testcase["body"],
            variables["data"]
        )
        self.assertEqual(
            parsed_testcase["headers"]["sum"],
            3
        )

    def test_load_testcases_by_path_files(self):
        testsets_list = []

        # absolute file path
        path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_hardcode.json')
        testset_list = testcase.load_testcases_by_path(path)
        self.assertEqual(len(testset_list), 1)
        self.assertIn("path", testset_list[0]["config"])
        self.assertEqual(testset_list[0]["config"]["path"], path)
        self.assertEqual(len(testset_list[0]["testcases"]), 3)
        testsets_list.extend(testset_list)

        # relative file path
        path = 'tests/data/demo_testset_hardcode.yml'
        testset_list = testcase.load_testcases_by_path(path)
        self.assertEqual(len(testset_list), 1)
        self.assertIn("path", testset_list[0]["config"])
        self.assertIn(path, testset_list[0]["config"]["path"])
        self.assertEqual(len(testset_list[0]["testcases"]), 3)
        testsets_list.extend(testset_list)

        # list/set container with file(s)
        path = [
            os.path.join(os.getcwd(), 'tests/data/demo_testset_hardcode.json'),
            'tests/data/demo_testset_hardcode.yml'
        ]
        testset_list = testcase.load_testcases_by_path(path)
        self.assertEqual(len(testset_list), 2)
        self.assertEqual(len(testset_list[0]["testcases"]), 3)
        self.assertEqual(len(testset_list[1]["testcases"]), 3)
        testsets_list.extend(testset_list)
        self.assertEqual(len(testsets_list), 4)

        for testset in testsets_list:
            for test in testset["testcases"]:
                self.assertIn('name', test)
                self.assertIn('request', test)
                self.assertIn('url', test['request'])
                self.assertIn('method', test['request'])

    def test_load_testcases_by_path_folder(self):
        # absolute folder path
        path = os.path.join(os.getcwd(), 'tests/data')
        testset_list_1 = testcase.load_testcases_by_path(path)
        self.assertGreater(len(testset_list_1), 4)

        # relative folder path
        path = 'tests/data/'
        testset_list_2 = testcase.load_testcases_by_path(path)
        self.assertEqual(len(testset_list_1), len(testset_list_2))

        # list/set container with file(s)
        path = [
            os.path.join(os.getcwd(), 'tests/data'),
            'tests/data/'
        ]
        testset_list_3 = testcase.load_testcases_by_path(path)
        self.assertEqual(len(testset_list_3), 2 * len(testset_list_1))

    def test_load_testcases_by_path_not_exist(self):
        # absolute folder path
        path = os.path.join(os.getcwd(), 'tests/data_not_exist')
        testset_list_1 = testcase.load_testcases_by_path(path)
        self.assertEqual(testset_list_1, [])

        # relative folder path
        path = 'tests/data_not_exist'
        testset_list_2 = testcase.load_testcases_by_path(path)
        self.assertEqual(testset_list_2, [])

        # list/set container with file(s)
        path = [
            os.path.join(os.getcwd(), 'tests/data_not_exist'),
            'tests/data_not_exist/'
        ]
        testset_list_3 = testcase.load_testcases_by_path(path)
        self.assertEqual(testset_list_3, [])

    def test_load_testcases_by_path_layered(self):
        path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_layer.yml')
        testsets_list = testcase.load_testcases_by_path(path)
        self.assertIn("variables", testsets_list[0]["config"])
        self.assertIn("request", testsets_list[0]["config"])
        self.assertIn("request", testsets_list[0]["testcases"][0])
        self.assertIn("url", testsets_list[0]["testcases"][0]["request"])
        self.assertIn("validators", testsets_list[0]["testcases"][0])

    def test_substitute_variables_with_mapping(self):
        content = {
            'request': {
                'url': '/api/users/$uid',
                'method': "$method",
                'headers': {'token': '$token'},
                'data': {
                    "null": None,
                    "true": True,
                    "false": False,
                    "empty_str": ""
                }
            }
        }
        mapping = {
            "$uid": 1000,
            "$method": "POST"
        }
        result = testcase.substitute_variables_with_mapping(content, mapping)
        self.assertEqual("/api/users/1000", result["request"]["url"])
        self.assertEqual("$token", result["request"]["headers"]["token"])
        self.assertEqual("POST", result["request"]["method"])
        self.assertIsNone(result["request"]["data"]["null"])
        self.assertTrue(result["request"]["data"]["true"])
        self.assertFalse(result["request"]["data"]["false"])
        self.assertEqual("", result["request"]["data"]["empty_str"])

    def test_load_test_dependencies(self):
        testcase.test_def_overall_dict = {}
        testcase.load_test_dependencies()
        self.assertTrue(testcase.test_def_overall_dict["loaded"])
        api_dict = testcase.test_def_overall_dict["api"]
        self.assertIn("get_token", api_dict)
        self.assertEqual("/api/get-token", api_dict["get_token"]["request"]["url"])
        self.assertIn("$user_agent", api_dict["get_token"]["function_meta"]["args"])
        self.assertIn("create_user", api_dict)

    def test_get_api_definition(self):
        api_info = testcase.get_test_definition("get_token", "api")
        self.assertEqual("/api/get-token", api_info["request"]["url"])
        self.assertIn("get_token", testcase.test_def_overall_dict["api"])

        with self.assertRaises(ApiNotFound):
            testcase.get_test_definition("api_not_exist", "api")
