#coding: utf-8
try:
    FileNotFoundError = FileNotFoundError
except NameError:
    FileNotFoundError = IOError

class MyBaseError(BaseException):
    pass

class ParamsError(MyBaseError):
    pass

class ResponseError(MyBaseError):
    pass

class ParseResponseError(MyBaseError):
    pass

class ValidationError(MyBaseError):
    pass

class FunctionNotFound(NameError):
    pass
