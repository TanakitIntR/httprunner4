# NOTICE: Generated By HttpRunner v3.0.8
# FROM: examples/httpbin/basic.yml

from httprunner import HttpRunner, Config, Step, RunRequest, RunTestCase


class TestCaseBasic(HttpRunner):
    config = Config("basic test with httpbin").base_url("https://httpbin.org/")

    teststeps = [
        Step(
            RunRequest("headers")
            .get("/headers")
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.headers.Host", "httpbin.org")
        ),
        Step(
            RunRequest("user-agent")
            .get("/user-agent")
            .validate()
            .assert_equal("status_code", 200)
            .assert_startswith('body."user-agent"', "python-requests")
        ),
        Step(
            RunRequest("get without params")
            .get("/get")
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.args", {})
        ),
        Step(
            RunRequest("get with params in url")
            .get("/get?a=1&b=2")
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.args", {"a": "1", "b": "2"})
        ),
        Step(
            RunRequest("get with params in params field")
            .get("/get")
            .with_params(**{"a": 1, "b": 2})
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.args", {"a": "1", "b": "2"})
        ),
        Step(
            RunRequest("set cookie")
            .get("/cookies/set?name=value")
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.cookies.name", "value")
        ),
        Step(
            RunRequest("extract cookie")
            .get("/cookies")
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal("body.cookies.name", "value")
        ),
        Step(
            RunRequest("post data")
            .post("/post")
            .with_headers(**{"Content-Type": "application/json"})
            .with_data("abc")
            .validate()
            .assert_equal("status_code", 200)
        ),
        Step(
            RunRequest("validate body length")
            .get("/spec.json")
            .validate()
            .assert_length_equal("body", 9)
        ),
    ]


if __name__ == "__main__":
    TestCaseBasic().test_start()
