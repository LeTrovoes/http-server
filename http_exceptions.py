class HTTPException(Exception):
    def __init__(self, status_code, status_text=None):
        self.status_code = status_code
        self.headers = []

    def addHeader(self, name, value):
        self.headers.append(Header(name, value))


# 4XX Exceptions
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
