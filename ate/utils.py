import hashlib
import hmac
import json
import os.path
import random
import re
import string

import yaml
from ate.exception import ParamsError

try:
    string_type = basestring
    PYTHON_VERSION = 2
except NameError:
    string_type = str
    PYTHON_VERSION = 3

SECRET_KEY = "DebugTalk"

def gen_random_string(str_len):
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(str_len))

def gen_md5(*str_args):
    return hashlib.md5("".join(str_args).encode('utf-8')).hexdigest()

def get_sign(*args):
    content = ''.join(args).encode('ascii')
    sign_key = SECRET_KEY.encode('ascii')
    sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
    return sign

def load_yaml_file(yaml_file):
    with open(yaml_file, 'r+') as stream:
        return yaml.load(stream)

def load_json_file(json_file):
    with open(json_file) as data_file:
        return json.load(data_file)

def load_testcases(testcase_file_path):
    file_suffix = os.path.splitext(testcase_file_path)[1]
    if file_suffix == '.json':
        return load_json_file(testcase_file_path)
    elif file_suffix in ['.yaml', '.yml']:
        return load_yaml_file(testcase_file_path)
    else:
        # '' or other suffix
        raise ParamsError("Bad testcase file name!")

def load_foler_files(folder_path):
    """ load folder path, return all files in list format.
    """
    file_list = []

    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_list.append(file_path)

    return file_list

def load_testcases_by_path(path):
    """ load testcases from file path
    @param path
        path could be in several type:
            - absolute/relative file path
            - absolute/relative folder path
            - list/set container with file(s) and/or folder(s)
    @return testcase sets list, each testset is corresponding to a file
        [
            {"name": "desc1", "config": {}, "testcases": [testcase11, testcase12]},
            {"name": "desc2", "config": {}, "testcases": [testcase21, testcase22, testcase23]},
        ]
    """
    if isinstance(path, (list, set)):
        testsets_list = []

        for file_path in set(path):
            _testsets_list = load_testcases_by_path(file_path)
            testsets_list.extend(_testsets_list)

        return testsets_list

    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)

    if os.path.isdir(path):
        files_list = load_foler_files(path)
        return load_testcases_by_path(files_list)

    elif os.path.isfile(path):
        testset = {
            "name": "",
            "config": {},
            "testcases": []
        }
        try:
            testcases_list = load_testcases(path)
        except ParamsError:
            return []

        for item in testcases_list:
            for key in item:
                if key == "config":
                    testset["config"] = item["config"]
                    testset["name"] = item["config"].get("name", "")
                elif key == "test":
                    testset["testcases"].append(item["test"])

        return [testset]

    else:
        return []

def query_json(json_content, query, delimiter='.'):
    """ Do an xpath-like query with json_content.
    @param (json_content) json_content
        json_content = {
            "ids": [1, 2, 3, 4],
            "person": {
                "name": {
                    "first_name": "Leo",
                    "last_name": "Lee",
                },
                "age": 29,
                "cities": ["Guangzhou", "Shenzhen"]
            }
        }
    @param (str) query
        "person.name.first_name"  =>  "Leo"
        "person.cities.0"         =>  "Guangzhou"
    @return queried result
    """
    stripped_query = query.strip(delimiter)
    if not stripped_query:
        return None

    try:
        for key in stripped_query.split(delimiter):
            if isinstance(json_content, list):
                key = int(key)
            json_content = json_content[key]
    except (KeyError, ValueError, IndexError):
        raise ParamsError("invalid query string in extract_binds!")

    return json_content

def match_expected(value, expected, comparator="eq"):
    """ check if value matches expected value.
    @param value: value that get from response.
    @param expected: expected result described in testcase
    @param comparator: compare method
    """
    try:
        if comparator in ["eq", "equals", "=="]:
            assert value == expected
        elif comparator in ["str_eq", "string_equals"]:
            assert str(value) == str(expected)
        elif comparator in ["ne", "not_equals"]:
            assert value != expected
        elif comparator in ["len_eq", "length_equal", "count_eq"]:
            assert len(value) == expected
        elif comparator in ["len_gt", "count_gt", "length_greater_than", "count_greater_than"]:
            assert len(value) > expected
        elif comparator in ["len_ge", "count_ge", "length_greater_than_or_equals", \
            "count_greater_than_or_equals"]:
            assert len(value) >= expected
        elif comparator in ["len_lt", "count_lt", "length_less_than", "count_less_than"]:
            assert len(value) < expected
        elif comparator in ["len_le", "count_le", "length_less_than_or_equals", \
            "count_less_than_or_equals"]:
            assert len(value) <= expected
        elif comparator in ["lt", "less_than"]:
            assert value < expected
        elif comparator in ["le", "less_than_or_equals"]:
            assert value <= expected
        elif comparator in ["gt", "greater_than"]:
            assert value > expected
        elif comparator in ["ge", "greater_than_or_equals"]:
            assert value >= expected
        elif comparator in ["contains"]:
            assert expected in value
        elif comparator in ["contained_by"]:
            assert value in expected
        elif comparator in ["regex"]:
            assert re.match(expected, value)
        elif comparator in ["str_len", "string_length"]:
            assert len(value) == int(expected)
        elif comparator in ["startswith"]:
            assert str(value).startswith(str(expected))
        else:
            raise ParamsError("comparator not supported!")

        return True
    except AssertionError:
        return False

def deep_update_dict(origin_dict, override_dict):
    """ update origin dict with override dict recursively
    e.g. origin_dict = {'a': 1, 'b': {'c': 2, 'd': 4}}
         override_dict = {'b': {'c': 3}}
    return: {'a': 1, 'b': {'c': 3, 'd': 4}}
    """
    for key, val in override_dict.items():
        if isinstance(val, dict):
            tmp = deep_update_dict(origin_dict.get(key, {}), val)
            origin_dict[key] = tmp
        else:
            origin_dict[key] = override_dict[key]

    return origin_dict
