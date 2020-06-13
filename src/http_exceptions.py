from http_response import Response
from http_constants import ALLOWED_METHODS

class HTTPException(Response, Exception):
    def __init__(self, status_code):
        Response.__init__(self, status_code)


class BadRequestException(HTTPException):
    '''A response for the case that the HTTP request doesn't follows the expected format'''
    def __init__(self):
        super().__init__(400)


class NotFoundException(HTTPException):
    '''A response for the case that the searched file isn't present on the provided path'''
    def __init__(self):
        super().__init__(404)


class MethodNotAllowedException(HTTPException):
    '''A response for the case that the HTTP request verb isn't supported by the server'''
    def __init__(self):
        super().__init__(405)
        self.addHeader('Allow', ', '.join(ALLOWED_METHODS))


class InternalServerErrorException(HTTPException):
    '''A response for any case a the error wasn't due to a client's mistake'''
    def __init__(self):
        super().__init__(500)
