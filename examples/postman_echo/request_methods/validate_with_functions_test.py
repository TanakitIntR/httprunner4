# NOTICE: Generated By HttpRunner v3.0.9
# FROM: examples/postman-echo/request.methods/validate_with_functions.yml

from httprunner import HttpRunner, Config, Step, RunRequest, RunTestCase


class TestCaseValidateWithFunctions(HttpRunner):
    config = (
        Config("request methods testcase: validate with functions")
        .variables(**{"foo1": "session_bar1"})
        .base_url("https://postman-echo.com")
        .verify(False)
    )

    teststeps = [
        Step(
            RunRequest("get with params")
            .with_variables(
                **{"foo1": "bar1", "foo2": "session_bar2", "sum_v": "${sum_two(1, 2)}"}
            )
            .get("/get")
            .with_params(**{"foo1": "$foo1", "foo2": "$foo2", "sum_v": "$sum_v"})
            .with_headers(**{"User-Agent": "HttpRunner/${get_httprunner_version()}"})
            .extract()
            .with_jmespath("body.args.foo2", "session_foo2")
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.args.sum_v", "3")
        ),
    ]


if __name__ == "__main__":
    TestCaseValidateWithFunctions().test_start()
