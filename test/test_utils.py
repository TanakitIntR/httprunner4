import os
import random
import requests
from ate import utils
from ate import exception
from .base import ApiServerUnittest

class TestUtils(ApiServerUnittest):

    def test_load_testcases_bad_filepath(self):
        testcase_file_path = os.path.join(os.getcwd(), 'test/data/demo')
        with self.assertRaises(exception.ParamsError):
            utils.load_testcases(testcase_file_path)

    def test_load_json_testcases(self):
        testcase_file_path = os.path.join(os.getcwd(), 'test/data/demo.json')
        testcases = utils.load_testcases(testcase_file_path)
        self.assertEqual(len(testcases), 2)
        self.assertIn('name', testcases[0])
        self.assertIn('request', testcases[0])
        self.assertIn('response', testcases[0])
        self.assertIn('url', testcases[0]['request'])
        self.assertIn('method', testcases[0]['request'])

    def test_load_yaml_testcases(self):
        testcase_file_path = os.path.join(os.getcwd(), 'test/data/demo.yml')
        testcases = utils.load_testcases(testcase_file_path)
        self.assertEqual(len(testcases), 2)
        self.assertIn('name', testcases[0])
        self.assertIn('request', testcases[0])
        self.assertIn('response', testcases[0])
        self.assertIn('url', testcases[0]['request'])
        self.assertIn('method', testcases[0]['request'])

    def test_parse_response_object_json(self):
        url = "http://127.0.0.1:5000/api/users"
        resp_obj = requests.get(url)
        parse_result = utils.parse_response_object(resp_obj)
        self.assertIn('status_code', parse_result)
        self.assertIn('headers', parse_result)
        self.assertIn('content', parse_result)
        self.assertIn('Content-Type', parse_result['headers'])
        self.assertIn('Content-Length', parse_result['headers'])
        self.assertIn('success', parse_result['content'])

    def test_parse_response_object_text(self):
        url = "http://127.0.0.1:5000/"
        resp_obj = requests.get(url)
        parse_result = utils.parse_response_object(resp_obj)
        self.assertIn('status_code', parse_result)
        self.assertIn('headers', parse_result)
        self.assertIn('content', parse_result)
        self.assertIn('Content-Type', parse_result['headers'])
        self.assertIn('Content-Length', parse_result['headers'])
        self.assertTrue(str, type(parse_result['content']))

    def test_diff_response_status_code_equal(self):
        status_code = random.randint(200, 511)
        url = "http://127.0.0.1:5000/status_code/%d" % status_code
        resp_obj = requests.get(url)
        expected_resp_json = {
            'status_code': status_code
        }
        diff_content = utils.diff_response(resp_obj, expected_resp_json)
        self.assertFalse(diff_content)

    def test_diff_response_status_code_not_equal(self):
        status_code = random.randint(200, 511)
        url = "http://127.0.0.1:5000/status_code/%d" % status_code
        resp_obj = requests.get(url)
        expected_resp_json = {
            'status_code': 512
        }
        diff_content = utils.diff_response(resp_obj, expected_resp_json)
        print('diff_content', diff_content)
        self.assertIn('value', diff_content['status_code'])
        self.assertIn('expected', diff_content['status_code'])
        self.assertEqual(diff_content['status_code']['value'], status_code)
        self.assertEqual(diff_content['status_code']['expected'], 512)
