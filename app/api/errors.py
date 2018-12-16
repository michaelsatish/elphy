from flask import jsonify

from . import api


class ApiException(Exception):
    status_code = None

    def __init__(self, message, payload=None):
        super().__init__(message)
        self.message = message
        self.payload = payload

    def to_dict(self):
        result_value = dict(self.payload or ())
        result_value['message'] = self.message
        return result_value


class BadRequest(ApiException):
    status_code = 400


class Unauthorized(ApiException):
    status_code = 401


class Forbidden(ApiException):
    status_code = 403


class NotFound(ApiException):
    status_code = 404


class InternalServerError(ApiException):
    status_code = 500


@api.errorhandler(BadRequest)
@api.errorhandler(Unauthorized)
@api.errorhandler(Forbidden)
@api.errorhandler(NotFound)
@api.errorhandler(InternalServerError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@api.errorhandler(Exception)
def api_error(e):
    return jsonify({
        'message': str(e)
    }), 500
