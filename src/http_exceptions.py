from http_response import Response
from http_constants import ALLOWED_METHODS

class HTTPException(Response, Exception):
    def __init__(self, status_code):
        Response.__init__(self, status_code)


class BadRequestException(HTTPException):
    def __init__(self):
        super().__init__(400)


class NotFoundException(HTTPException):
    def __init__(self):
        super().__init__(404)


class MethodNotAllowedException(HTTPException):
    def __init__(self):
        super().__init__(405)
        self.addHeader('Allow', ', '.join(ALLOWED_METHODS))


class InternalServerErrorException(HTTPException):
    def __init__(self):
        super().__init__(500)
