# NOTICE: Generated By HttpRunner v3.0.8
# FROM: examples/httpbin/hooks.yml

from httprunner import HttpRunner, Config, Step, RunRequest, RunTestCase


class TestCaseHooks(HttpRunner):
    config = Config("basic test with httpbin").base_url("${get_httpbin_server()}")

    teststeps = [
        Step(
            RunRequest("headers")
            .with_variables(**{"a": 123})
            .get("/headers")
            .validate()
            .assert_equal("status_code", 200)
            .assert_contained_by("body.headers.Host", "${get_httpbin_server()}")
        ),
        Step(
            RunRequest("alter response")
            .get("/headers")
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.headers.Host", "httpbin.org")
        ),
    ]


if __name__ == "__main__":
    TestCaseHooks().test_start()
