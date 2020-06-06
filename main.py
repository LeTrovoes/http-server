import socket as sc
import os.path
import os
import datetime as date
from urllib.parse import urlparse
import traceback
from http_exceptions import *

PUBLIC_DIRECTORY = './public'

SERVER_PORT = int(os.environ['PORT']) if 'PORT' in os.environ else 3000

HTTP_CODES_TEXT = {
    200: 'OK',
    400: 'Bad Request',
    404: 'Not Found',
    405: 'Method Not Allowed',
    500: 'Internal Server Error'
}

HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
ALLOWED_METHODS = ['GET', 'HEAD', 'OPTIONS']


def get_path_from_target(target: str) -> str:
    path = urlparse(target).path
    path = path.strip('/')

    if path == '':
        path = 'index.html'
    path = os.path.join(PUBLIC_DIRECTORY, path)

    return path


def does_path_exists(path: str) -> bool:
    return os.path.isfile(path)


def read_file(path: str) -> bytes:
    with open(path, 'rb') as f:
        buffer = f.read()
    return buffer


def get_file_last_modified(path: str) -> date:
    lastmodified = os.stat(path).st_mtime
    lastmodified = date.datetime.utcfromtimestamp(lastmodified)
    return lastmodified


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
        self.addHeader(
            'Date', date.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))

    def addHeader(self, name, value):
        self.headers.append(Header(name, value))

    def setBody(self, content, type='text/plain', lastmodified=None, encoding='utf-8'):
        self.body = content
        self.addHeader('Content-Type', f'{type}')
        self.addHeader('Content-Length', str(len(self.body)))
        if lastmodified:
            self.addHeader(
                'Last Modified', lastmodified.strftime("%a, %d %b %Y %H:%M:%S GMT"))


    def getMessage(self) -> bytes:
        message = "HTTP/1.1 %d %s\n" % (self.status_code, self.status_text)
        for header in self.headers:
            message += header.toString()
        message += '\n'
        message = message.encode()
        if self.body:
            message += self.body
        return message


class OkResponse(Response):  # o arquivo já vai vir junto com a resposta? ou a função do read vai so no main?
    def __init__(self):
        super().__init__(200)

class OptionResponse(Response):
    def __init__(self):
        super().__init__(200)
        self.addHeader('Allow', ', '.join(ALLOWED_METHODS))


class InternalServerErrorResponse(Response):
    def __init__(self):
        super().__init__(500)


def get_mime_type(file_type):
    file_type = file_type.lower()
    if file_type == 'html':
        return 'text/html'
    elif file_type == 'png':
        return 'image/png'
    else:
        return 'text/plain'


def handleHTTPVersion(version):
    if version.upper() != 'HTTP/1.1':
        raise BadRequestException()


def handleMethod(method):
    method = method.upper()

    if method not in HTTP_METHODS:
        raise BadRequestException()

    if method not in ALLOWED_METHODS:
        raise MethodNotAllowedException()

    return method


def handleRequest(req) -> Response:
    method, target, version, *rest = req.decode().split()

    handleHTTPVersion(version)

    method = handleMethod(method)

    if method == 'OPTIONS':
        return OptionResponse()

    path = get_path_from_target(target)

    if not does_path_exists(path):
        return NotFoundResponse()

    content = read_file(path)
    last_modified = get_file_last_modified(path)
    file_type = path.split('.')[-1]
    mime_type = get_mime_type(file_type)
    res = OkResponse()

    if method == 'GET':
        res.setBody(content, mime_type, last_modified)

    return res


def handleConnection(conn, addr):
    req = conn.recv(8192)  # TODO: better handling
    try:
        res = handleRequest(req).getMessage()
    except Exception as e:
        print(e)
        traceback.print_stack(e)
        res = InternalServerErrorResponse().getMessage()

    conn.send(res)
    conn.close()


if __name__ == '__main2__':
    socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
    socket.bind(('', SERVER_PORT))
    socket.listen(1)

    print('Server is listening at port', SERVER_PORT)

    while True:
        handleConnection(socket.accept())
