import inspect
from typing import Text, Any, Union, Callable

from httprunner.schema import (
    TConfig,
    TStep,
    TRequest,
    MethodEnum,
    TestCase,
)


class Config(object):
    def __init__(self, name: Text):
        self.__name = name
        self.__variables = {}
        self.__base_url = ""
        self.__verify = False

        caller_frame = inspect.stack()[1]
        self.__path = caller_frame.filename

    @property
    def name(self):
        return self.__name

    @property
    def path(self):
        return self.__path

    def variables(self, **variables) -> "Config":
        self.__variables.update(variables)
        return self

    def base_url(self, base_url: Text) -> "Config":
        self.__base_url = base_url
        return self

    def verify(self, verify: bool) -> "Config":
        self.__verify = verify
        return self

    def perform(self) -> TConfig:
        return TConfig(
            name=self.__name,
            base_url=self.__base_url,
            verify=self.__verify,
            variables=self.__variables,
            path=self.__path,
        )


class StepValidation(object):
    def __init__(self, step: TStep):
        self.__t_step = step

    def assert_equal(self, jmes_path: Text, expected_value: Any) -> "StepValidation":
        self.__t_step.validators.append({"eq": [jmes_path, expected_value]})
        return self

    def assert_greater_than(
        self, jmes_path: Text, expected_value: Any
    ) -> "StepValidation":
        self.__t_step.validators.append({"gt": [jmes_path, expected_value]})
        return self

    def assert_less_than(
        self, jmes_path: Text, expected_value: Any
    ) -> "StepValidation":
        self.__t_step.validators.append({"lt": [jmes_path, expected_value]})
        return self

    def perform(self) -> TStep:
        return self.__t_step


class StepExtraction(object):
    def __init__(self, step: TStep):
        self.__t_step = step

    def with_jmespath(self, jmes_path: Text, var_name: Text) -> "StepExtraction":
        self.__t_step.extract[var_name] = jmes_path
        return self

    # def with_regex(self):
    #     # TODO: extract response html with regex
    #     pass
    #
    # def with_jsonpath(self):
    #     # TODO: extract response json with jsonpath
    #     pass

    def validate(self) -> StepValidation:
        return StepValidation(self.__t_step)

    def perform(self) -> TStep:
        return self.__t_step


class RequestWithOptionalArgs(object):
    def __init__(self, step: TStep):
        self.__t_step = step

    def with_params(self, **params) -> "RequestWithOptionalArgs":
        self.__t_step.request.params.update(params)
        return self

    def with_headers(self, **headers) -> "RequestWithOptionalArgs":
        self.__t_step.request.headers.update(headers)
        return self

    def with_cookies(self, **cookies) -> "RequestWithOptionalArgs":
        self.__t_step.request.cookies.update(cookies)
        return self

    def with_data(self, data) -> "RequestWithOptionalArgs":
        self.__t_step.request.data = data
        return self

    def set_timeout(self, timeout: float) -> "RequestWithOptionalArgs":
        self.__t_step.request.timeout = timeout
        return self

    def set_verify(self, verify: bool) -> "RequestWithOptionalArgs":
        self.__t_step.request.verify = verify
        return self

    def set_allow_redirects(self, allow_redirects: bool) -> "RequestWithOptionalArgs":
        self.__t_step.request.allow_redirects = allow_redirects
        return self

    # def hooks(self):
    #     pass

    def extract(self) -> StepExtraction:
        return StepExtraction(self.__t_step)

    def validate(self) -> StepValidation:
        return StepValidation(self.__t_step)

    def perform(self) -> TStep:
        return self.__t_step


class RunRequest(object):
    def __init__(self, name: Text):
        self.__t_step = TStep(name=name)

    def with_variables(self, **variables) -> "RunRequest":
        self.__t_step.variables.update(variables)
        return self

    def get(self, url: Text) -> RequestWithOptionalArgs:
        self.__t_step.request = TRequest(method=MethodEnum.GET, url=url)
        return RequestWithOptionalArgs(self.__t_step)

    def post(self, url: Text) -> RequestWithOptionalArgs:
        self.__t_step.request = TRequest(method=MethodEnum.POST, url=url)
        return RequestWithOptionalArgs(self.__t_step)

    def put(self, url: Text) -> RequestWithOptionalArgs:
        self.__t_step.request = TRequest(method=MethodEnum.PUT, url=url)
        return RequestWithOptionalArgs(self.__t_step)

    def head(self, url: Text) -> RequestWithOptionalArgs:
        self.__t_step.request = TRequest(method=MethodEnum.HEAD, url=url)
        return RequestWithOptionalArgs(self.__t_step)

    def delete(self, url: Text) -> RequestWithOptionalArgs:
        self.__t_step.request = TRequest(method=MethodEnum.DELETE, url=url)
        return RequestWithOptionalArgs(self.__t_step)

    def options(self, url: Text) -> RequestWithOptionalArgs:
        self.__t_step.request = TRequest(method=MethodEnum.OPTIONS, url=url)
        return RequestWithOptionalArgs(self.__t_step)

    def patch(self, url: Text) -> RequestWithOptionalArgs:
        self.__t_step.request = TRequest(method=MethodEnum.PATCH, url=url)
        return RequestWithOptionalArgs(self.__t_step)


class RunTestCase(object):
    def __init__(self, name: Text):
        self.__t_step = TStep(name=name)

    def with_variables(self, **variables) -> "RunTestCase":
        self.__t_step.variables.update(variables)
        return self

    def call(self, testcase: Callable):
        self.__t_step.testcase = testcase
        return self

    def perform(self) -> TStep:
        return self.__t_step


class Step(object):
    def __init__(
        self,
        step: Union[
            StepValidation, StepExtraction, RequestWithOptionalArgs, RunTestCase
        ],
    ):
        self.__t_step = step.perform()

    @property
    def request(self) -> TRequest:
        return self.__t_step.request

    @property
    def testcase(self) -> TestCase:
        return self.__t_step.testcase

    def perform(self) -> TStep:
        return self.__t_step
