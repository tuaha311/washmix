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


class InternalServerError(WMError):
    @classmethod
    def http_status_code(cls):
        return 500
