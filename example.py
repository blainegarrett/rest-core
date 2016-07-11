""" Example Application """

import os
import sys
import webapp2
import json

# Bootstrap the external libs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'external'))

from rest_core import handlers


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


routes = []
app = webapp2.WSGIApplication(routes, debug=True)
app.error_handlers[404] = handle_404
