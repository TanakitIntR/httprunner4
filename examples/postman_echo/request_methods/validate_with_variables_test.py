# NOTE: Generated By HttpRunner v3.1.0
# FROM: examples/postman_echo/request_methods/validate_with_variables.yml

from httprunner import HttpRunner, Config, Step, RunRequest, RunTestCase


class TestCaseValidateWithVariables(HttpRunner):
    config = (
        Config("request methods testcase: validate with variables")
        .variables(**{"foo1": "session_bar1"})
        .base_url("https://postman-echo.com")
        .verify(False)
    )

    teststeps = [
        Step(
            RunRequest("get with params")
            .with_variables(**{"foo1": "bar1", "foo2": "session_bar2"})
            .get("/get")
            .with_params(**{"foo1": "$foo1", "foo2": "$foo2"})
            .with_headers(**{"User-Agent": "HttpRunner/3.0"})
            .extract()
            .with_jmespath("body.args.foo2", "session_foo2")
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.args.foo1", "$foo1")
            .assert_equal("body.args.foo2", "$foo2")
        ),
        Step(
            RunRequest("post raw text")
            .with_variables(**{"foo1": "hello world", "foo3": "$session_foo2"})
            .post("/post")
            .with_headers(
                **{"User-Agent": "HttpRunner/3.0", "Content-Type": "text/plain"}
            )
            .with_data(
                "This is expected to be sent back as part of response body: $foo1-$foo3."
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal(
                "body.data",
                "This is expected to be sent back as part of response body: hello world-$foo3.",
            )
        ),
        Step(
            RunRequest("post form data")
            .with_variables(**{"foo1": "bar1", "foo2": "bar2"})
            .post("/post")
            .with_headers(
                **{
                    "User-Agent": "HttpRunner/3.0",
                    "Content-Type": "application/x-www-form-urlencoded",
                }
            )
            .with_data("foo1=$foo1&foo2=$foo2")
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.form.foo1", "$foo1")
            .assert_equal("body.form.foo2", "$foo2")
        ),
    ]


if __name__ == "__main__":
    TestCaseValidateWithVariables().test_start()
