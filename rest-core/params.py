from voluptuous import Schema
from google.appengine.datastore.datastore_query import Cursor
import datetime
from pytz import timezone


class ResourceParams(object):
    def __init__(self, schema):
        self.param_schema = schema

    def from_dict(self, input_params):
        """
        :param input_params dict:
        """

        schema = Schema(self.param_schema)
        validated_params = schema(input_params)

        return validated_params


def coerce_to_cursor(val):
    """
    Validate that val is None or a db.Cursor
    """

    if not val:
        return None

    cursor = Cursor(urlsafe=val)
    return cursor


def coerce_to_datetime(dtstr):
    """
    Helper to convert a input datetime string to a UTC datetime
    """

    if not dtstr:
        return None

    try:
        fmt = '%Y-%m-%dT%H:%M:%SZ'
        dt = datetime.datetime.strptime(dtstr, fmt)
    except ValueError:
        # Attempt full day method
        fmt = '%Y-%m-%d'
        dt = datetime.datetime.strptime(dtstr, fmt)

    dt = timezone('UTC').localize(dt)
    return dt  # .replace(tzinfo=None)


def coerce_from_datetime(dt):
    """
    Helper to convert a input UTC datetime to a string
    """
    if not dt:
        return None  # Should this be an empty str?
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
