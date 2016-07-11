""" A collection of helper methods """

import re
import hashlib
import json
import base64
from google.appengine.ext import ndb
from constants import API_WHITELIST_DOMAINS, API_WHITELIST_RULES


SEPARATOR = chr(30)
INTPREFIX = chr(31)


def get_resource_id_from_key(key):
    """
    Convert a ndb.Key() into a portable `str` resource id
    :param key: An instance of `ndb.Key`
    """

    pair_strings = []

    pairs = key.pairs()

    for pair in pairs:
        kind = unicode(pair[0])
        key_or_id = pair[1]

        if isinstance(key_or_id, (int, long)):
            key_or_id = unicode(INTPREFIX + unicode(key_or_id))

        pair_strings.append(kind + SEPARATOR + key_or_id)

    buff = SEPARATOR.join(pair_strings)
    encoded = base64.urlsafe_b64encode(buff)
    encoded = encoded.replace('=', '')
    return encoded


def get_key_from_resource_id(resource_id):
    """
    Convert a portable `str` resource id into a ndb.Key
    :param resource_id: A `str` resource_id
    """

    # Add padding back on as needed...
    modulo = len(resource_id) % 4
    if modulo != 0:
        resource_id += ('=' * (4 - modulo))

    # decode the url safe resource id
    decoded = base64.urlsafe_b64decode(str(resource_id))

    key_pairs = []
    bits = decoded.split(SEPARATOR)

    for bit in bits:
        if (bit[0] == INTPREFIX):
            bit = int(bit[1:])
        key_pairs.append(bit)

    return ndb.Key(*key_pairs)


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
