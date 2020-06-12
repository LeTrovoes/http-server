from datetime import datetime
from http_constants import *


class Header:
    '''
    A class that represents a Header of one HTTP response

    Attributes
    ----------
    name : str
        header type
    value : str
        information provided by the header

    Methods
    -------
    toString()
        returns the string of the header with the correct format and a new line
    '''

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def toString(self):
        return self.name + ': ' + self.value + '\n'


class Response:
    '''
    General class of a HTTP response

    This class can be used as the base to generate any possible HTTP response

    Attributes
    ----------
    default_headers : list
        contain the tuples that generates the headers common to all responses
    status_code : int
        the status code as documented in the RFC 7231
    status_text : str, optional
        the meaning of the status code provided (default is the value in HTTP_CODES_TEXT)
    body : bytes, optional
        the body present at the end of the HTTP response (default is None)
    headers : list
        the Header objects already generated

    Methods
    -------
    addHeader(name, value)
        Create a new Header object and add it to headers
    setContentHeaders(content_type='application/octet-stream',
                      content_length=0, last_modified=None)
        Add all headers that corresponds to a file information to headers
    setBody(content, content_type, last_modified)
        Add a file to body and calls setContentHeaders with its information
    getMessage()
        Create the encoded message with all the headers and the body if provided
    '''

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

    def setContentHeaders(
        self,
        content_type: str = 'application/octet-stream',
        content_length: int = 0,
        last_modified = None
    ):
        self.addHeader('Content-Type', content_type)
        self.addHeader('Content-Length', str(content_length))
        if last_modified:
            self.addHeader('Last Modified', last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT"))

    def setBody(self, content, content_type, last_modified):
        self.body = content
        self.setContentHeaders(content_type, len(self.body), last_modified)

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
