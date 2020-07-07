import json


class WMError(Exception):
    def __init__(self, error_message=None, error_code=None, additional_info=None):
        """
        :param error_message: str | error message mapping to custom error code
        :param error_code: int | custom error code that points to specific error message
        :param additional_info: dict | extra error information for the client
        """
        Exception.__init__(self)
        self.message = error_message
        self.status_code = None
        self.additional_info = additional_info

        if error_code is not None:
            self.status_code = error_code

    def to_dict(self):
        """
        Method will create a dict object containing all provided error details
        :rtype: dict
        """
        error_dict = {"error": {}}
        if self.status_code:
            error_dict["error"]["status_code"] = self.status_code
        if self.message:
            error_dict["error"]["message"] = self.message
        if self.additional_info:
            for k, v in self.additional_info.items():
                error_dict["error"][k] = v
        return error_dict

    @classmethod
    def http_status_code(cls):
        return 500


class InvalidUsage(WMError):
    @classmethod
    def http_status_code(cls):
        return 400


class UnauthorizedError(WMError):
    @classmethod
    def http_status_code(cls):
        return 401


class ForbiddenError(WMError):
    @classmethod
    def http_status_code(cls):
        return 403


class NotFoundError(WMError):
    @classmethod
    def http_status_code(cls):
        return 404


class InternalServerError(WMError):
    @classmethod
    def http_status_code(cls):
        return 500


def register_errors(app):
    @errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        return handle_error(error, "Invalid usage")

    @errorhandler(UnauthorizedError)
    def handle_unauthorized_error(error):
        return handle_error(error, "Unauthorized access")

    @errorhandler(ForbiddenError)
    def handle_forbidden_error(error):
        return handle_error(error, "Forbidden access")

    @errorhandler(NotFoundError)
    def handle_unauthorized_error(error):
        return handle_error(error, "Resource not found")

    @errorhandler(InternalServerError)
    def handle_server_error(error):
        return handle_error(error, "Server error")

    def handle_error(error, message):
        """
        :type error: WMError
        :param message:
        :return:
        """
        return json.dumps(error.to_dict()), error.http_status_code()
