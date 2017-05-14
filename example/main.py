""" Example Application """

import os
import sys
import webapp2
import json

# Bootstrap the external libs
EXAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(EXAMPLE_DIR, '../external'))
sys.path.insert(0, os.path.join(EXAMPLE_DIR, '../rest_core'))
sys.path.insert(0, EXAMPLE_DIR)

def serve_response(response, status, result, messages=None):
    """
    Serve a response
    """

    payload = {'status': status, 'results': result, 'messages': messages}
    response.set_status(status)
    response.headers['content-type'] = 'application/json'
    response.write(json.dumps(payload))


def handle_404(request, response, exception):
    """
    Top Level Route handler for 404
    """

    err = 'Rest endpoint not found or unavailable'

    serve_response(response, 404, None, messages=[err])


routes = [
    (r'/posts', 'example.handlers.PostsApiHandler'),
    (r'/posts/([a-zA-Z0-9-_]+)', 'example.handlers.PostDetailApiHandler'),
]


app = webapp2.WSGIApplication(routes, debug=True)
app.error_handlers[404] = handle_404
