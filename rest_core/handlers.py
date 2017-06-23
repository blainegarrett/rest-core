"""
Rest Controller Base Handlers
"""

import webapp2
import json
import traceback
import sys
import os
import logging

from constants import API_DEFAULT_ORIGIN
import errors
from resources import Resource
from params import ResourceParams
import utils as rest_utils


class RestHandlerBase(webapp2.RequestHandler):
    """
    Base Class for All Rest Endpoints
    """

    def is_same_origin(self):
        """
        Helper Method to determine if referrer is the same as the host
        This is to support 'dumb' REST permissions to prevent attacking REST Services
        """

        # TODO: REWORK THIS TO OPERATE ON SETTINGS

        # If local sdk, allow
        if os.environ['SERVER_SOFTWARE'].startswith('Development'):
            return True

        # TODO: Check whitelist as part of this instead of referer
        # if not self.request.referer:
        #     return False
        # return urlparse(self.request.referer)[1] == self.request.host
        return True

    def get_param_schema(self):
        """
        If you want query params, you must implement this
        """
        return {}

    def validate_params(self):
        """
        Run Validation on query params
        """

        param_schema = self.get_param_schema()
        self.cleaned_params = ResourceParams(param_schema).from_dict(self.params)

    def validate_payload(self):  # aka Form.clean
        """
        Validate the request payload against the rest rules
        This only works for a single payload entity, not a list...
        """

        rules = self.get_rules()
        self.cleaned_data = Resource(None, rules).from_dict(self.data)

    def dispatch(self):
        """
        Dispatcher for checking various things
        """

        try:
            self.data = {}
            self.cleaned_data = {}
            self.params = {}
            self.cleaned_params = {}

            # Do basic access checks
            if not self.is_same_origin():
                raise errors.RestError('Invalid referrer: %s' % self.request.referer)

            # Process Request Payload
            rest_utils.apply_middleware(self.request, 'process_request')

            # Convert: body into native format
            if len(self.request.body) > 0:
                if 'application/json' in self.request.headers['Content-Type']:
                    self.data = json.loads(self.request.body)
                elif 'multipart/form-data' in self.request.headers['Content-Type']:
                    # TODO: We prob don't want this? it's for uploading files...
                    self.data = self.request.POST.mixed()
                    logging.error(self.data)

            # Query parameters
            self.params = self.request.GET.mixed()
            self.validate_params()

            # Validate incoming payload
            if self.request.method in ('POST', 'PUT'):
                self.validate_payload()

            # Attempt to run handler
            super(RestHandlerBase, self).dispatch()

            # Process Response Payload
            rest_utils.apply_middleware(self.request, 'process_response')

        except errors.DoesNotExistException, e:
            self.serve_404(unicode(e))
        except errors.AuthenticationException, e:
            self.serve_error(e, status=401)
        except errors.PermissionException, e:
            self.serve_error(e, status=403)
        except errors.MethodNotAllowed, e:
            self.serve_error(e, status=405)
        except Exception, e:
            self.serve_error(e)  # status=500 for clarity?

    def options(self, *args, **kwargs):
        """
        Called for ajax calls for most browsers in X-Origin
        """
        self.serve_response(200, [])

    def serve_success(self, result, extra_fields={}):
        """Serve up a 200 response"""
        self.serve_response(200, result, extra_fields=extra_fields)

    def serve_404(self, msg='Endpoint Not Found'):
        """Serve up a 404 Response """
        self.serve_response(404, [], messages=msg)

    def serve_error(self, exception, status=500):
        """Serve up a Exception Response"""
        # TODO: Pass in exception stack
        # TODO: Figure out how to communicate  retryable exceptions, etc

        exc_type, exc_value, exc_traceback = sys.exc_info()
        formatted_lines = traceback.format_exc().splitlines()

        self.serve_response(status, formatted_lines, messages=[str(exception)])
        logging.exception(exception)

    def serve_response(self, status, result, messages=None, extra_fields={}):
        """Serve the response"""

        allow_header_values = "Authorization, Origin, X-Requested-With, Content-Type, Accept"

        if (not isinstance(messages, list)):
            messages = [messages]

        self.response.set_status(status)

        # Determine origin bits
        request_origin = self.request.headers.get('Origin') or self.request.referer
        response_origin = API_DEFAULT_ORIGIN

        origin_in_whitelist = rest_utils.is_origin_in_whitelist(request_origin)
        if origin_in_whitelist:
            response_origin = request_origin  # Input origin is good, so passthru

        # TODO: Validate that extra_fields doesn't contain bad props - collisions
        payload = extra_fields
        payload.update({'status': status, 'results': result, 'messages': messages})

        self.response.headers['Access-Control-Allow-Origin'] = response_origin
        self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
        self.response.headers['Access-Control-Allow-Credentials'] = 'true'
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Headers'] = allow_header_values

        if (self.request.GET.get('pretty')):
            output_json = json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            output_json = json.dumps(payload, sort_keys=True)

        self.response.write(output_json)
