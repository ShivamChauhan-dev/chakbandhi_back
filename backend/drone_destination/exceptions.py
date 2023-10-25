from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException, MethodNotAllowed, NotAuthenticated, Throttled, PermissionDenied, ValidationError
from .codes import ErrorCode
from django.http import Http404
from django.core import exceptions
from django.db import IntegrityError
from http import HTTPStatus
from rest_framework_simplejwt.exceptions import InvalidToken


class ErrorCodeException(APIException):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, error_code: ErrorCode, http_status_code=None, detail=None):
        self.error_code = error_code
        self.status_code = http_status_code
        message = detail if detail is not None else error_code.description
        super().__init__(message, code=http_status_code)


class FieldsException(APIException):
    def __init__(self, fields: dict, message, http_status_code=None):
        super().__init__(message, code=http_status_code)
        self.fields = fields
        self.error_code = ErrorCode.FIELDS_ERROR


def custom_exception_handler(exc, context):
    response: Response = exception_handler(exc, context)
    if isinstance(exc, MethodNotAllowed):
        response = request_method_not_allowed(response, [])
    elif isinstance(exc, Throttled):
        response = request_throttled(response, exc)
    elif isinstance(exc, ValidationError) and isinstance(exc.detail, dict):
        response = on_fields_missing(missing_fields=exc.detail, response=response)
    elif isinstance(exc, exceptions.ValidationError):
        response = on_fields_missing(missing_fields=exc.error_dict, response=response)
    elif isinstance(exc, ErrorCodeException):
        response = request_http_error_response(response, exc.error_code)
    elif isinstance(exc, IntegrityError):
        response = request_http_error_response(response, ErrorCode.FIELDS_ERROR, message=str(exc.args.__getitem__(0)))
    elif isinstance(exc, exceptions.ObjectDoesNotExist) or isinstance(exc, Http404):
        return Response(data={"error": error_data(ErrorCode.NOT_FOUND, message=str(exc.args.__getitem__(0)))},
                        status=ErrorCode.NOT_FOUND.get_http_status_code())
    elif isinstance(exc, NotAuthenticated):
        response = request_http_error_response(response, error_code=ErrorCode.AUTH_FAILED, message=exc.detail)
    elif isinstance(exc, PermissionDenied):
        response = request_http_error_response(response, error_code=ErrorCode.NOT_PERMITTED, message=exc.detail)
    elif isinstance(exc, InvalidToken):
        response = request_http_error_response(response, error_code=ErrorCode.INVALID_AUTH_TOKEN, message=exc.detail)
    elif exc is not None and response is not None:
        response = request_http_error_response(response, error_code=ErrorCode.INTERNAL_ERROR, message=exc.detail)

    if response is None:
        error_code = ErrorCode.INTERNAL_ERROR
        message = str(exc)
        return Response(data={"error": error_data(error_code, message=message)},
                        status=error_code.get_http_status_code())

    return response


def request_method_not_allowed(response, allowed_method: list) -> Response:
    return request_http_error_response(response, ErrorCode.INVALID_METHOD,
                                       {"method": 'Only ' + str(allowed_method) + ' request '
                                                                                  'permitted'})


def request_throttled(response, exc: Throttled) -> Response:
    return request_http_error_response(response, ErrorCode.REQUEST_THROTTLED,
                                       {"wait": exc.wait}, message=exc.detail)


def on_fields_missing(response, missing_fields: dict) -> Response:
    return request_http_error_response(response, ErrorCode.FIELDS_ERROR, fields=missing_fields)


def request_http_error_response(response: Response, error_code: ErrorCode, fields: dict = None,
                                message: str = None) -> Response:
    if message is None:
        if error_code.is_FIELDS_ERROR() and fields is not None:
            message = f'Error in {list(fields.keys())} field.'
        else:
            message = error_code.description

    # status_code = response.status_code

    if response is None:
        response = Response()
        response.status_code = error_code.get_http_status_code()

    response.data = {
        "error": error_data(error_code=error_code, fields=fields, message=message, status_code=response.status_code)}
    return response


def error_data(error_code: ErrorCode, fields: dict = None, message: str = None, status_code: int = None) -> dict:
    fields_array = []

    if fields is not None:
        for key, value in fields.items():
            fields_array.append({"field": key, "message": value})

    if status_code is None:
        status_code = error_code.get_http_status_code()

    return {
        "message": message,
        "status": status_code,
        "error": error_code.phrase,
        "error_code": error_code.value,
        "description": error_code.description,
        "fields": fields_array
    }


def handler500(request, exception=None, *args, **kwargs):
    return custom_exception_handler(exception, request)
