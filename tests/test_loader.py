import os
import unittest

from httprunner import exceptions, loader, utils


class TestFileLoader(unittest.TestCase):

    def test_load_yaml_file_file_format_error(self):
        yaml_tmp_file = "tests/data/tmp.yml"
        # create empty yaml file
        with open(yaml_tmp_file, 'w') as f:
            f.write("")

        with self.assertRaises(exceptions.FileFormatError):
            loader.load_yaml_file(yaml_tmp_file)

        os.remove(yaml_tmp_file)

        # create invalid format yaml file
        with open(yaml_tmp_file, 'w') as f:
            f.write("abc")

        with self.assertRaises(exceptions.FileFormatError):
            loader.load_yaml_file(yaml_tmp_file)

        os.remove(yaml_tmp_file)


    def test_load_json_file_file_format_error(self):
        json_tmp_file = "tests/data/tmp.json"
        # create empty file
        with open(json_tmp_file, 'w') as f:
            f.write("")

        with self.assertRaises(exceptions.FileFormatError):
            loader.load_json_file(json_tmp_file)

        os.remove(json_tmp_file)

        # create empty json file
        with open(json_tmp_file, 'w') as f:
            f.write("{}")

        with self.assertRaises(exceptions.FileFormatError):
            loader.load_json_file(json_tmp_file)

        os.remove(json_tmp_file)

        # create invalid format json file
        with open(json_tmp_file, 'w') as f:
            f.write("abc")

        with self.assertRaises(exceptions.FileFormatError):
            loader.load_json_file(json_tmp_file)

        os.remove(json_tmp_file)

    def test_load_testcases_bad_filepath(self):
        testcase_file_path = os.path.join(os.getcwd(), 'tests/data/demo')
        with self.assertRaises(exceptions.FileNotFound):
            loader.load_file(testcase_file_path)

    def test_load_json_testcases(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_hardcode.json')
        testcases = loader.load_file(testcase_file_path)
        self.assertEqual(len(testcases), 3)
        test = testcases[0]["test"]
        self.assertIn('name', test)
        self.assertIn('request', test)
        self.assertIn('url', test['request'])
        self.assertIn('method', test['request'])

    def test_load_yaml_testcases(self):
        testcase_file_path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_hardcode.yml')
        testcases = loader.load_file(testcase_file_path)
        self.assertEqual(len(testcases), 3)
        test = testcases[0]["test"]
        self.assertIn('name', test)
        self.assertIn('request', test)
        self.assertIn('url', test['request'])
        self.assertIn('method', test['request'])

    def test_load_csv_file_one_parameter(self):
        csv_file_path = os.path.join(
            os.getcwd(), 'tests/data/user_agent.csv')
        csv_content = loader.load_file(csv_file_path)
        self.assertEqual(
            csv_content,
            [
                {'user_agent': 'iOS/10.1'},
                {'user_agent': 'iOS/10.2'},
                {'user_agent': 'iOS/10.3'}
            ]
        )

    def test_load_csv_file_multiple_parameters(self):
        csv_file_path = os.path.join(
            os.getcwd(), 'tests/data/account.csv')
        csv_content = loader.load_file(csv_file_path)
        self.assertEqual(
            csv_content,
            [
                {'username': 'test1', 'password': '111111'},
                {'username': 'test2', 'password': '222222'},
                {'username': 'test3', 'password': '333333'}
            ]
        )

    def test_load_folder_files(self):
        folder = os.path.join(os.getcwd(), 'tests')
        file1 = os.path.join(os.getcwd(), 'tests', 'test_utils.py')
        file2 = os.path.join(os.getcwd(), 'tests', 'data', 'demo_binds.yml')

        files = loader.load_folder_files(folder, recursive=False)
        self.assertNotIn(file2, files)

        files = loader.load_folder_files(folder)
        self.assertIn(file2, files)
        self.assertNotIn(file1, files)

        files = loader.load_folder_files(folder)
        api_file = os.path.join(os.getcwd(), 'tests', 'api', 'basic.yml')
        self.assertIn(api_file, files)

        files = loader.load_folder_files("not_existed_foulder", recursive=False)
        self.assertEqual([], files)

        files = loader.load_folder_files(file2, recursive=False)
        self.assertEqual([], files)

    def test_load_dot_env_file(self):
        self.assertNotIn("PROJECT_KEY", os.environ)
        loader.load_dot_env_file("tests/data/test.env")
        self.assertIn("PROJECT_KEY", os.environ)
        self.assertEqual(os.environ["UserName"], "debugtalk")

    def test_load_env_path_not_exist(self):
        with self.assertRaises(exceptions.FileNotFound):
            loader.load_dot_env_file("not_exist.env")


class TestSuiteLoader(unittest.TestCase):

    def setUp(self):
        loader.overall_def_dict = {
            "api": {},
            "suite": {}
        }

    def test_load_test_dependencies(self):
        loader.load_test_dependencies()
        overall_def_dict = loader.overall_def_dict
        self.assertIn("get_token", overall_def_dict["api"])
        self.assertIn("create_and_check", overall_def_dict["suite"])

    def test_load_api_file(self):
        loader.load_api_file("tests/api/basic.yml")
        overall_api_def_dict = loader.overall_def_dict["api"]
        self.assertIn("get_token",overall_api_def_dict)
        self.assertEqual("/api/get-token", overall_api_def_dict["get_token"]["request"]["url"])
        self.assertIn("$user_agent", overall_api_def_dict["get_token"]["function_meta"]["args"])
        self.assertEqual(len(overall_api_def_dict["get_token"]["validate"]), 3)

    def test_load_test_file_suite(self):
        loader.load_api_file("tests/api/basic.yml")
        testset = loader.load_test_file("tests/suite/create_and_get.yml")
        self.assertEqual(testset["config"]["name"], "create user and check result.")
        self.assertEqual(len(testset["testcases"]), 3)
        self.assertEqual(testset["testcases"][0]["name"], "make sure user $uid does not exist")
        self.assertEqual(testset["testcases"][0]["request"]["url"], "/api/users/$uid")

    def test_load_test_file_testcase(self):
        loader.load_test_dependencies()
        testset = loader.load_test_file("tests/testcases/smoketest.yml")
        self.assertEqual(testset["config"]["name"], "smoketest")
        self.assertEqual(testset["config"]["path"], "tests/testcases/smoketest.yml")
        self.assertIn("device_sn", testset["config"]["variables"][0])
        self.assertEqual(len(testset["testcases"]), 8)
        self.assertEqual(testset["testcases"][0]["name"], "get token")

    def test_get_block_by_name(self):
        loader.load_test_dependencies()
        ref_call = "get_user($uid, $token)"
        block = loader._get_block_by_name(ref_call, "api")
        self.assertEqual(block["request"]["url"], "/api/users/$uid")
        self.assertEqual(block["function_meta"]["func_name"], "get_user")
        self.assertEqual(block["function_meta"]["args"], ['$uid', '$token'])

    def test_get_block_by_name_args_mismatch(self):
        loader.load_test_dependencies()
        ref_call = "get_user($uid, $token, $var)"
        with self.assertRaises(exceptions.ParamsError):
            loader._get_block_by_name(ref_call, "api")

    def test_override_block(self):
        loader.load_test_dependencies()
        def_block = loader._get_block_by_name("get_token($user_agent, $device_sn, $os_platform, $app_version)", "api")
        test_block = {
            "name": "override block",
            "variables": [
                {"var": 123}
            ],
            'request': {
                'url': '/api/get-token', 'method': 'POST', 'headers': {'user_agent': '$user_agent', 'device_sn': '$device_sn', 'os_platform': '$os_platform', 'app_version': '$app_version'}, 'json': {'sign': '${get_sign($user_agent, $device_sn, $os_platform, $app_version)}'}},
            'validate': [
                {'eq': ['status_code', 201]},
                {'len_eq': ['content.token', 32]}
            ]
        }

        utils._override_block(def_block, test_block)
        self.assertEqual(test_block["name"], "override block")
        self.assertIn({'check': 'status_code', 'expect': 201, 'comparator': 'eq'}, test_block["validate"])
        self.assertIn({'check': 'content.token', 'comparator': 'len_eq', 'expect': 32}, test_block["validate"])

    def test_get_test_definition_api(self):
        loader.load_test_dependencies()
        api_def = loader._get_test_definition("get_headers", "api")
        self.assertEqual(api_def["request"]["url"], "/headers")
        self.assertEqual(len(api_def["setup_hooks"]), 2)
        self.assertEqual(len(api_def["teardown_hooks"]), 1)

        with self.assertRaises(exceptions.ApiNotFound):
            loader._get_test_definition("get_token_XXX", "api")

    def test_get_test_definition_suite(self):
        loader.load_test_dependencies()
        api_def = loader._get_test_definition("create_and_check", "suite")
        self.assertEqual(api_def["config"]["name"], "create user and check result.")

        with self.assertRaises(exceptions.SuiteNotFound):
            loader._get_test_definition("create_and_check_XXX", "suite")

    def test_load_testcases_by_path_files(self):
        testsets_list = []

        # absolute file path
        path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_hardcode.json')
        testset_list = loader.load_testcases(path)
        self.assertEqual(len(testset_list), 1)
        self.assertIn("path", testset_list[0]["config"])
        self.assertEqual(testset_list[0]["config"]["path"], path)
        self.assertEqual(len(testset_list[0]["testcases"]), 3)
        testsets_list.extend(testset_list)

        # relative file path
        path = 'tests/data/demo_testset_hardcode.yml'
        testset_list = loader.load_testcases(path)
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
        testset_list = loader.load_testcases(path)
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
        loader.load_test_dependencies()
        # absolute folder path
        path = os.path.join(os.getcwd(), 'tests/data')
        testset_list_1 = loader.load_testcases(path)
        self.assertGreater(len(testset_list_1), 4)

        # relative folder path
        path = 'tests/data/'
        testset_list_2 = loader.load_testcases(path)
        self.assertEqual(len(testset_list_1), len(testset_list_2))

        # list/set container with file(s)
        path = [
            os.path.join(os.getcwd(), 'tests/data'),
            'tests/data/'
        ]
        testset_list_3 = loader.load_testcases(path)
        self.assertEqual(len(testset_list_3), 2 * len(testset_list_1))

    def test_load_testcases_by_path_not_exist(self):
        # absolute folder path
        path = os.path.join(os.getcwd(), 'tests/data_not_exist')
        with self.assertRaises(exceptions.FileNotFound):
            loader.load_testcases(path)

        # relative folder path
        path = 'tests/data_not_exist'
        with self.assertRaises(exceptions.FileNotFound):
            loader.load_testcases(path)

        # list/set container with file(s)
        path = [
            os.path.join(os.getcwd(), 'tests/data_not_exist'),
            'tests/data_not_exist/'
        ]
        with self.assertRaises(exceptions.FileNotFound):
            loader.load_testcases(path)

    def test_load_testcases_by_path_layered(self):
        loader.load_test_dependencies()
        path = os.path.join(
            os.getcwd(), 'tests/data/demo_testset_layer.yml')
        testsets_list = loader.load_testcases(path)
        self.assertIn("variables", testsets_list[0]["config"])
        self.assertIn("request", testsets_list[0]["config"])
        self.assertIn("request", testsets_list[0]["testcases"][0])
        self.assertIn("url", testsets_list[0]["testcases"][0]["request"])
        self.assertIn("validate", testsets_list[0]["testcases"][0])
