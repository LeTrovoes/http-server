from datetime import datetime
from http_constants import *


class Header:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def toString(self):
        return self.name + ': ' + self.value + '\n'


class Response:
    default_headers = [
        ("Connection", "Close"),
        ("Server", "Sadao")
    ]

    def __init__(self, status_code, status_text=None):
        self.status_code = status_code
        self.status_text = status_text or HTTP_CODES_TEXT[status_code]
        self.body = None
        self.headers = [Header(*header) for header in self.default_headers]
        self.addHeader('Date', datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))

    def addHeader(self, name, value):
        self.headers.append(Header(name, value))

    def setBody(self, content, contentType='application/octet-stream', lastmodified=None):
        self.body = content
        self.addHeader('Content-Type', contentType)
        self.addHeader('Content-Length', str(len(self.body)))
        if lastmodified:
            self.addHeader('Last Modified', lastmodified.strftime("%a, %d %b %Y %H:%M:%S GMT"))

    def getMessage(self) -> bytes:
        message = "HTTP/1.1 %d %s\n" % (self.status_code, self.status_text)
        for header in self.headers:
            message += header.toString()
        message += '\n'
        message = message.encode()
        if self.body:
            message += self.body
        return message


class OkResponse(Response):
    def __init__(self):
        super().__init__(200)


class OptionResponse(Response):
    def __init__(self):
        super().__init__(200)
        self.addHeader('Allow', ', '.join(ALLOWED_METHODS))
