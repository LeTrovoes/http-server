HTTP_CODES_TEXT = {
    200: 'OK',
    400: 'Bad Request',
    404: 'Not Found',
    405: 'Method Not Allowed',
    500: 'Internal Server Error'
}

HTTP_METHODS = {
    'GET': 'GET',
    'POST': 'POST',
    'PUT': 'PUT',
    'DELETE': 'DELETE',
    'HEAD': 'HEAD',
    'OPTIONS': 'OPTIONS'
}

ALLOWED_METHODS = [
    HTTP_METHODS['GET'],
    HTTP_METHODS['HEAD'],
    HTTP_METHODS['OPTIONS']
]
