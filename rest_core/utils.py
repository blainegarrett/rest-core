""" A collection of helper methods """

import re
import hashlib
import json
from constants import API_WHITELIST_DOMAINS, API_WHITELIST_RULES

import rest_core_settings as settings


SEPARATOR = chr(30)
INTPREFIX = chr(31)


def is_origin_in_whitelist(domain):
    """
    Check if a given domain (starting with protocol) is in our white list
    :param domain: A `str` of protocol://domain

    TODO: Make this more generic for when this is a pip installable library
    """

    if not domain:
        return False

    # Check against explicit list
    if domain in API_WHITELIST_DOMAINS:
        return True

    # Check against rules
    for rule in API_WHITELIST_RULES:
        matches = re.match(rule, domain)

        if matches:
            return True

    return False


def create_request_key(prefix, params_dict):
    """
    Method to hash a set of url params into a key suitable for caching
    :param prefix: A `str` to prefix the key with
    :param params_dict: A flat dictionary of url params

    TODO: Can we consider permissions, etc once we get into stuff like that?
    TODO: WE need to ensure this matches the JS side eventually. Determine if device dependent?
    """

    param_keys = params_dict.keys()

    # Sort the dict keys alphabetically
    param_keys = sorted(param_keys, key=unicode.lower)

    #
    sorted_params = []
    for param_key in param_keys:
        sorted_params.append((param_key, params_dict[param_key]))

    # Sort the keys
    json_str = json.dumps(sorted_params, separators=(',', ':'))

    cache_stamp = str(hashlib.md5(json_str).hexdigest())

    if prefix:
        cache_stamp = "%s_%s" % (prefix, cache_stamp)

    return cache_stamp


def path_to_reference(path):
    """
    Convert an object path reference to a reference.
    # Note: This is glorked from furious
        https://github.com/Workiva/furious/blob/master/furious/job_utils.py
    """
    path = str(path)

    if '.' not in path:
        try:
            return globals()["__builtins__"][path]
        except KeyError:
            try:
                return getattr(globals()["__builtins__"], path)
            except AttributeError:
                pass

        try:
            return globals()[path]
        except KeyError:
            pass

        raise Exception(
            'Unable to find function "%s".' % (path,))

    module_path, function_name = path.rsplit('.', 1)

    try:
        module = __import__(name=module_path,
                            fromlist=[function_name])
    except ImportError:
        module_path, class_name = module_path.rsplit('.', 1)

        module = __import__(name=module_path, fromlist=[class_name])
        module = getattr(module, class_name)

    try:
        return getattr(module, function_name)
    except AttributeError:
        raise Exception(
            'Unable to find function "%s".' % (path,))


def apply_middleware(request, func_name):
    """
    Given a callback hook funcname,
    #TODO: This should cache the imports
    """

    if not (hasattr(settings, 'REST_MIDDLEWARE_CLASSES') and settings.REST_MIDDLEWARE_CLASSES):
        return

    for middleware_path in settings.REST_MIDDLEWARE_CLASSES:
        klass = path_to_reference(middleware_path)
        if hasattr(klass, func_name):
            getattr(klass, func_name)(request)

    return True
