import logging
from collections import OrderedDict

from ate import exception, response, testcase, utils
from ate.client import HttpSession
from ate.context import Context


class Runner(object):

    def __init__(self, http_client_session=None):
        self.http_client_session = http_client_session
        self.context = Context()
        testcase.load_test_dependencies()

    def init_config(self, config_dict, level):
        """ create/update context variables binds
        @param (dict) config_dict
        @param (str) level, "testset" or "testcase"
        testset:
            {
                "name": "smoke testset",
                "path": "tests/data/demo_testset_variables.yml",
                "requires": [],         # optional
                "function_binds": {},   # optional
                "import_module_items": [],  # optional
                "variables": [],   # optional
                "request": {
                    "base_url": "http://127.0.0.1:5000",
                    "headers": {
                        "User-Agent": "iOS/2.8.3"
                    }
                }
            }
        testcase:
            {
                "name": "testcase description",
                "requires": [],         # optional
                "function_binds": {},   # optional
                "import_module_items": [],  # optional
                "variables": [],   # optional
                "request": {
                    "url": "/api/get-token",
                    "method": "POST",
                    "headers": {
                        "Content-Type": "application/json"
                    }
                },
                "json": {
                    "sign": "f1219719911caae89ccc301679857ebfda115ca2"
                }
            }
        @param (str) context level, testcase or testset
        """
        # convert keys in request headers to lowercase
        config_dict = utils.lower_config_dict_key(config_dict)

        self.context.init_context(level)
        self.context.config_context(config_dict, level)

        request_config = config_dict.get('request', {})
        parsed_request = self.context.get_parsed_request(request_config, level)

        base_url = parsed_request.pop("base_url", None)
        self.http_client_session = self.http_client_session or HttpSession(base_url)

        return parsed_request

    def _run_test(self, testcase):
        """ run single testcase.
        @param (dict) testcase
            {
                "name": "testcase description",
                "times": 3,
                "requires": [],         # optional, override
                "function_binds": {},   # optional, override
                "variables": [],        # optional, override
                "request": {
                    "url": "http://127.0.0.1:5000/api/users/1000",
                    "method": "POST",
                    "headers": {
                        "Content-Type": "application/json",
                        "authorization": "$authorization",
                        "random": "$random"
                    },
                    "body": '{"name": "user", "password": "123456"}'
                },
                "extract": [], # optional
                "validators": [],    # optional
                "setup": [],         # optional
                "teardown": []       # optional
            }
        @return True or raise exception during test
        """
        parsed_request = self.init_config(testcase, level="testcase")

        try:
            url = parsed_request.pop('url')
            method = parsed_request.pop('method')
            group_name = parsed_request.pop("group", None)
        except KeyError:
            raise exception.ParamsError("URL or METHOD missed!")

        run_times = int(testcase.get("times", 1))
        extractors = testcase.get("extract") \
            or testcase.get("extract_binds", [])
        validators = testcase.get("validators", [])
        setup_actions = testcase.get("setup", [])
        teardown_actions = testcase.get("teardown", [])

        def setup_teardown(actions):
            for action in actions:
                self.context.exec_content_functions(action)

        for _ in range(run_times):
            setup_teardown(setup_actions)

            resp = self.http_client_session.request(
                method,
                url,
                name=group_name,
                **parsed_request
            )
            resp_obj = response.ResponseObject(resp)

            extracted_variables_mapping = resp_obj.extract_response(extractors)
            self.context.bind_variables(extracted_variables_mapping, level="testset")

            try:
                resp_obj.validate(validators, self.context.get_testcase_variables_mapping())
            except (exception.ParamsError, exception.ResponseError, exception.ValidationError):
                logging.error("Exception occured.")
                logging.error("HTTP request kwargs: \n{}".format(parsed_request))
                logging.error("HTTP response content: \n{}".format(resp.text))
                raise

            setup_teardown(teardown_actions)

        return True

    def _run_testset(self, testset, variables_mapping=None):
        """ run single testset, including one or several testcases.
        @param
            (dict) testset
                {
                    "name": "testset description",
                    "config": {
                        "name": "testset description",
                        "requires": [],
                        "function_binds": {},
                        "variables": [],
                        "request": {}
                    },
                    "testcases": [
                        {
                            "name": "testcase description",
                            "variables": [], # optional, override
                            "request": {},
                            "extract": {},  # optional
                            "validators": {}      # optional
                        },
                        testcase12
                    ]
                }
            (dict) variables_mapping:
                passed in variables mapping, it will override variables in config block

        @return (dict) test result of testset
            {
                "success": True,
                "output": {}    # variables mapping
            }
        """
        success = True
        config_dict = testset.get("config", {})

        variables = config_dict.get("variables", [])
        variables_mapping = variables_mapping or {}
        config_dict["variables"] = utils.override_variables_binds(variables, variables_mapping)

        self.init_config(config_dict, level="testset")
        testcases = testset.get("testcases", [])
        for testcase in testcases:
            try:
                assert self._run_test(testcase)
            except AssertionError:
                success = False

        output_variables_list = config_dict.get("output", [])

        return {
            "success": success,
            "output": self.generate_output(output_variables_list)
        }

    def run(self, path, mapping=None):
        """ run specified testset path or folder path.
        @param
            path: path could be in several type
                - absolute/relative file path
                - absolute/relative folder path
                - list/set container with file(s) and/or folder(s)
            (dict) mapping:
                passed in variables mapping, it will override variables in config block
        """
        success = True
        mapping = mapping or {}
        output = {}
        testsets = testcase.load_testcases_by_path(path)
        for testset in testsets:
            try:
                result = self._run_testset(testset, mapping)
                assert result["success"]
                output.update(result["output"])
            except AssertionError:
                success = False

        return {
            "success": success,
            "output": output
        }

    def generate_output(self, output_variables_list):
        """ generate and print output
        """
        variables_mapping = self.context.get_testcase_variables_mapping()
        output = {
            variable: variables_mapping[variable]
            for variable in output_variables_list
        }
        utils.print_output(output)

        return output
