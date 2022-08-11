from bottle import run, get

PORT = 8000


@get('/')
def get_token():
    return {}


run(host='localhost', port=PORT, debug=True, reloader=True)
