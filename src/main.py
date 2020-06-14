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

# Selects the port the server will be initialized
# The value is defined based on the value PORT on the environment variables
# This could be done on initialization as in the follow example:
#   'PORT=2000 python3 src/main.py'
# If not provided defaults to 3000
SERVER_PORT = int(os.environ['PORT']) if 'PORT' in os.environ else 3000


def get_path_from_target(target: str) -> str:
    '''Get the path from the target provided

    Separates the path from the target and add it to the default public directory location.
    If the path is only '/' returns the path from the default page index.html
    '''

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
    '''Generates an OK response with the file on the body and its information headers'''
    content = read_file(path)
    last_modified = get_file_last_modified(path)
    file_type = path.split('.')[-1]
    mime_type = get_mime_type(file_type)
    res = OkResponse()
    res.setBody(content, mime_type, last_modified)
    return res


def handleHEAD(path):
    '''Generates an OK response containing only the headers regarding the file's information'''
    file_type = path.split('.')[-1]
    mime_type = get_mime_type(file_type)
    file_size = get_file_size(path)
    last_modified = get_file_last_modified(path)
    res = OkResponse()
    res.setContentHeaders(mime_type, file_size, last_modified)
    return res


def handleOPTIONS(path):
    '''Generates a response with all possible HTTP verbs for the provided path'''
    return OptionResponse()


def handleHTTPVersion(version):
    '''Checks if the HTTP version provided is the 1.1 as it is the only supported by the server

    Raises
    ------
    BadRequestException
        A response for the case that the HTTP request doesn't follows the expected format
    '''

    if version.upper() != 'HTTP/1.1':
        raise BadRequestException()


def handleMethod(method):
    '''Checks if the HTTP method provided is valid and supported by the server

    Raises
    ------
    BadRequestException
        A response for the case that the HTTP request doesn't follows the expected format
    MethodNotAllowedException
        A response for the case that the HTTP request verb isn't supported by the server

    '''

    method = method.upper()

    if method not in HTTP_METHODS:
        raise BadRequestException()

    if method not in ALLOWED_METHODS:
        raise MethodNotAllowedException()

    return method


def handleRequest(req) -> Response:
    '''Generates an appropriated response for the provided request

    Raises
    ------
    BadRequestException
        A response for the case that the HTTP request doesn't follows the expected format
    MethodNotAllowedException
        A response for the case that the HTTP request verb isn't supported by the server
    NotFoundException
        A response for the case that the requested file isn't present on the provided path
    '''

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
    '''Receives the HTTP request and send an appropriated response

    Receive an message of limited size, tries to perform the action desired by
    the client and sends the response

    If any error is found during the process, it sends an notifying response to
    the client instead

    After handling the request, closes the connection with the client
    '''

    print(f'Handling connection from {addr[0]}')
    req = conn.recv(8192)  # TODO: better handling
    try:
        res = handleRequest(req).getMessage()
    except HTTPException as http_exception:
        res = http_exception.getMessage()
    except Exception:
        traceback.print_exc()
        res = 'HTTP/1.1 500 Internal Server Error\n'.encode()

    conn.send(res)
    conn.close()


if __name__ == '__main__':
    socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
    socket.bind(('', SERVER_PORT))
    # number of the requests that awaits on the stack for a connection
    socket.listen(1)

    print('Server is listening at port', SERVER_PORT)

    # Awaits until a client requests to make a connection with the server
    # Then, creates a connection and calls the function that handles the
    # client's HTTP message
    while True:
        conn, addr = socket.accept()
        handleConnection(conn, addr)
