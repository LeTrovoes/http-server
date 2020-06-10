from datetime import datetime
import os
import os.path
import socket as sc
import traceback
from urllib.parse import urlparse

from http_constants import *
from http_response import *
from http_exceptions import *

PUBLIC_DIRECTORY = './public'

SERVER_PORT = int(os.environ['PORT']) if 'PORT' in os.environ else 3000


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


def get_file_last_modified(path: str):
    lastmodified = os.stat(path).st_mtime
    lastmodified = datetime.utcfromtimestamp(lastmodified)
    return lastmodified


def get_file_size(path: str) -> int:
    return os.path.getsize(path)


def get_mime_type(file_type):
    file_type = file_type.lower()
    if file_type == 'html':
        return 'text/html'
    elif file_type == 'png':
        return 'image/png'
    else:
        return 'text/plain'


def handleGET(path):
    content = read_file(path)
    last_modified = get_file_last_modified(path)
    file_type = path.split('.')[-1]
    mime_type = get_mime_type(file_type)
    res = OkResponse()
    res.setBody(content, mime_type, last_modified)
    return res


def handleHEAD(path):
    file_type = path.split('.')[-1]
    mime_type = get_mime_type(file_type)
    file_size = get_file_size(path)
    last_modified = get_file_last_modified(path)
    res = OkResponse()
    res.setContentHeaders(mime_type, file_size, last_modified)
    return res


def handleOPTIONS(path):
    return OptionResponse()


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
    path = get_path_from_target(target)

    if not does_path_exists(path):
        raise NotFoundException()

    if method == HTTP_METHODS['GET']:
        res = handleGET(path)
    elif method == HTTP_METHODS['HEAD']:
        res = handleHEAD(path)
    elif method == HTTP_METHODS['OPTIONS']:
        res = handleOPTIONS(path)

    return res


def handleConnection(conn, addr):
    print(f'Handling connection from {addr[0]}')
    req = conn.recv(8192)  # TODO: better handling
    try:
        res = handleRequest(req).getMessage()
    except HTTPException as http_exception:
        res = http_exception.getMessage()
    except Exception as e:
        traceback.print_stack(e)
        res = 'HTTP/1.1 500 Internal Server Error\n'.encode()

    conn.send(res)
    conn.close()


if __name__ == '__main__':
    socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
    socket.bind(('', SERVER_PORT))
    socket.listen(1)

    print('Server is listening at port', SERVER_PORT)

    while True:
        conn, addr = socket.accept()
        handleConnection(conn, addr)
