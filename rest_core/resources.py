"""
REST Resource and Field Types

Note: This is designed to work similar django Forms - try to keep it that way
"""

import voluptuous

from google.appengine.ext import ndb
import logging
from models import Model
from params import coerce_to_datetime, coerce_from_datetime
from utils import get_resource_id_from_key
from utils import get_key_from_resource_id

NON_FIELD_ERRORS = '__all__'
VALID_RESORCE_TYPES = (ndb.Model, dict)  # None: is also allowed


class RestValueException(Exception):
    """
    Value Error for a Rest rule - similar to django.forms.ValidationError
    """

    def __init__(self, field, value, error):
        self.field = field
        self.value = value
        self.error = error

    def __str__(self):
        return 'Invalid value "%s" for "prop" %s. Error: %s' % (self.value, self.field.key,
                                                                self.error)


class RequiredFieldError(Exception):
    pass


class UnknownFieldError(Exception):
    pass


class UnsupportedFieldProp(Exception):
    pass


class OutputOnlyError(Exception):
    pass


class ResourceList(object):
    """
    List Endpoint helper
    TODO: Do this yet
    """


class Resource(object):
    """
    Object to represent a REST Resource
    """

    def __init__(self, obj, fields):
        """
        :param obj:
            Instance of ndb.Model, dict or None when attempting to validate a resource payload
        """

        # Step 1: Make sure entities is a list
        if not obj:
            obj = None

        # Step 2: Do some type checking
        if obj and not isinstance(obj, VALID_RESORCE_TYPES):
            err = 'Resource() requires a instance of %s or None. Received %s, %s.'
            raise TypeError(err % (VALID_RESORCE_TYPES, type(obj), obj))

        self.resource_type = 'NonDefinedClass'

        if (obj and isinstance(obj, Model)):
            self.resource_type = obj.get_kind()
        elif (obj and isinstance(obj, ndb.Model)):
            self.resource_type = obj.key.kind()

        if not (isinstance(fields, list)):
            err = 'Resource requires list. Received %s, %s.'
            raise TypeError(err % (type(list), fields))

        # Step 3:  Set params as instance properties
        self.obj = obj
        self.fields = fields

        self.errors = {}
        self.cleaned_data = {}

    def from_dict(self, data):
        """
        Loads in a Rest Resource from a dictionary of a values

        TODO: Add validation at this level too
        TODO: Throw OutputOnlyError if a field is output_only=True
        """

        # First validate that all input keys are allowed input fields
        allowed_input_field_keys = []
        required_input_field_keys = []
        self.cleaned_data = {}

        for field in self.fields:
            if not field.output_only:  # or allowed...
                allowed_input_field_keys.append(field.key)

            if field.required:
                required_input_field_keys.append(field.key)

        allowed_input_field_keys = set(allowed_input_field_keys)
        required_input_field_keys = set(required_input_field_keys)

        given_field_keys = set(data.keys())

        for key in given_field_keys.difference(allowed_input_field_keys):
            # TODO: Collect these and present them as a single error dict
            raise UnknownFieldError('key "%s" is not an allowed input field for a resource.' % key)

        # Next validate that required keys are not abscent
        for key in required_input_field_keys.difference(given_field_keys):
            # TODO: Collect these and present them as a single error dict
            raise RequiredFieldError('key "%s" is a required input field for a resource.' % key)

        # Next Validate the various properties
        for field in self.fields:
            if (not field.output_only) and field.key in data:
                value = field.to_resource(data)
                self.cleaned_data[field.key] = value

        return self.cleaned_data

    def to_dict(self, verbose=False):
        """
        Dumps a rest Resource to a dictionary of values
        """

        result = {}

        obj = self.obj
        if not obj:
            return result

        # Keep track of if we excluded anything because of verbose, etc
        has_excluded_props = False

        for field in self.fields:
            if not field.verbose_only or verbose:
                result[field.key] = field.from_resource(obj, field.key)
            else:
                has_excluded_props = True

        result['resource_type'] = self.resource_type
        result['_meta'] = {'is_verbose': not has_excluded_props,
                           'resource_type': self.resource_type}
        return result


class RestField(object):
    """
    Baseclass for a specific field for a Rest Resource.
    """

    def __init__(self, prop, verbose_only=False, always=True, validator=None, output_only=False,
                 input_only=False, required=False):

        self.key = None  # This is the dict key for Resource dict

        self.prop = prop
        self.verbose_only = verbose_only
        self.always = always

        self.validator = validator
        self.input_only = input_only
        self.output_only = output_only
        self.required = required  # Required on input

        if isinstance(self.prop, ndb.model.Property):
            self.key = self.key or self.prop._name
        elif isinstance(self, (ResourceUrlField, ResourceIdField)):
            self.key = self.prop
        elif isinstance(self.prop, basestring):
            self.key = self.prop
        elif isinstance(self.prop, property):
            self.key = self.prop.fget.__name__
        else:
            raise UnsupportedFieldProp('Rest Property not supported %s', prop)

    def validate(self, value):
        # TODO: I don't think this is in use yet...

        # TODO: Have this throw errors django forms style
        # TODO: This does not yet look at self.required

        if self.validator:
            try:
                value = voluptuous.Schema(self.validator, required=self.required)(value)
            except Exception, e:
                raise RestValueException(self, value, e)

        return value

    def from_resource(self, obj, field):
        """
        Default handler for properties

        TODO: Arg field should be self.key ?
        TODO: Are from_resource and to_resource conceptually named the opposite?
        TODO: Raise a uniform Error
        """

        if isinstance(obj, dict):
            return obj.get(field, None)
        return getattr(obj, field, None)

    def to_resource(self, data):
        """
        Input a field to a dict value
        """

        # Attempt to retrieve the value
        value = data.get(self.key, 'not_present')

        # If it wasn't in the payload and it is required
        if ((value == 'not_present') and self.required):
            raise RequiredFieldError('Field "%s" is a required input field.' % self.key)

        # If it was in the payload but undefined and it is required (note this is bool fase safe)
        if (value is None or value == '') and self.required:
            raise RequiredFieldError('Field "%s" is a required input field.' % self.key)

        # Check if value is an input only prop
        if not value == 'not_present' and self.output_only:
            raise OutputOnlyError('Field "%s" is not an allowed input field.' % self.key)

        # Validate Type
        value = self.validate(value)

        return value


class ResourceUrlField(RestField):
    """
    Field to populate the endpoint url to get the full resource
    TODO: This should always be output only
    """

    def __init__(self, url_template, **kwargs):
        prop = 'resource_url'  # This is sort of a dummy value
        self.url_template = url_template
        super(ResourceUrlField, self).__init__(prop, **kwargs)

    def from_resource(self, obj, field):
        """
        Outout a field to dic value
        """
        if (obj and isinstance(obj, Model)):
            return self.url_template % obj.id
        else:
            return self.url_template % get_resource_id_from_key(obj.key)


class ResourceIdField(RestField):
    """
    Field to populate the resource key of the resource
    TODO: This should always be output only?
    """

    def __init__(self, **kwargs):
        prop = 'resource_id'
        super(ResourceIdField, self).__init__(prop, **kwargs)

    def from_resource(self, obj, field):
        """
        Outout a field to dic value
        """

        # Native Model
        if (obj and isinstance(obj, Model)):
            return obj.id

        # NDB Model
        try:
            resource_id = get_resource_id_from_key(obj.key)
        except:
            logging.error('Attempting to get ResourceID for a non ndb Entity...')
            logging.error(obj)
            resource_id = None
        return resource_id


class ResourceField(RestField):
    """
    Resource Field - similar to a Reference Property
    """

    def __init__(self, prop, resource_id_prop, resource_rules, **kwargs):
        self.resource_id_prop = resource_id_prop
        self.resource_rules = resource_rules
        super(ResourceField, self).__init__(prop, **kwargs)

    def from_resource(self, obj, field):
        """
        Resolve a REST resource from an entity
        """

        resource_id = super(ResourceField, self).from_resource(obj, self.resource_id_prop)

        if not resource_id:
            return None

        # Resolve Entity
        resource_entity = None
        if hasattr(obj, self.key):
            resource_entity = getattr(obj, self.key, None)
        else:
            logging.error('Reference prop `%s` was not bulk dereferenced.' % self.key)
            try:
                resource_key = get_key_from_resource_id(resource_id)
                resource_entity = resource_key.get()
            except ValueError:
                vars = (resource_id, self.key)
                logging.error('Failed to convert resource id %s to a key for prop %s.' % vars)
                logging.error(obj)
                return None

        return Resource(resource_entity, self.resource_rules).to_dict()


class UploadField(RestField):
    """
    Rest Resource Helper for Upload field.
    TODO: This needs review and to probably be moved to file services
    """

    def __init__(self, prop, **kwargs):
        super(UploadField, self).__init__(prop, **kwargs)

    def to_resource(self, data):
        val = super(UploadField, self).to_resource(data)

        if val:
            return ndb.GeoPt(lat=val['lat'], lon=val['lon'])
        return None

    def from_resource(self, obj, field):
        """
        Outout a field to dic value
        """

        # FieldStorage(u'the_file', u'title_bar.jpg') evals to false for some reason...

        val = super(UploadField, self).from_resource(obj, field)

        if not val:
            return None

        return {'lat': val.lat, 'lon': val.lon}


def json_validator(val):
    """
    Validate str is json

    TODO: Why did I leave this commented out?
    """
    import json

    if not val:
        return ''

    # try:
    result = json.loads(val)
    # except Exception:
    #    raise voluptuous.Invalid("Invalid JSON Structure")
    return val


class JSONField(RestField):
    """
    Field to input and validated a string of json
    """

    def __init__(self, prop, **kwargs):
        kwargs['validator'] = json_validator

        super(JSONField, self).__init__(prop, **kwargs)


class BooleanField(RestField):
    """
    Boolean field
    """

    def to_resource(self, data):
        val = super(BooleanField, self).to_resource(data)

        if val in ['', 'false', 'False', None, False]:
            return False
        else:
            return True

    def from_resource(self, obj, field):
        """
        Outout a field to dict value
        """

        val = super(BooleanField, self).from_resource(obj, field)

        if not val:
            return False

        if val == True:
            return True

        raise Exception(val)


class GeoField(RestField):
    """
    Field to support a Geo coordinate property
    """

    def __init__(self, prop, **kwargs):
        super(GeoField, self).__init__(prop, **kwargs)

    def to_resource(self, data):
        val = super(GeoField, self).to_resource(data)

        # Could be a single dict or a list of dicts

        if val:
            if (isinstance(val, list)):
                return [ndb.GeoPt(lat=pt['lat'], lon=pt['lon']) for pt in val]
            return ndb.GeoPt(lat=val['lat'], lon=val['lon'])
        return None

    def from_resource(self, obj, field):
        """
        Outout a field to dic value
        """

        val = super(GeoField, self).from_resource(obj, field)

        if not val:
            return None

        return [{'lat': pt.lat, 'lon': pt.lon} for pt in val]


class SlugField(RestField):
    """
    Field to support a slug - must match input format
    """

    def __init__(self, prop, **kwargs):
        kwargs['validator'] = voluptuous.Coerce(str)

        super(SlugField, self).__init__(prop, **kwargs)


class DatetimeField(RestField):
    """
    Field to support a Geo coordinate property
    """

    def __init__(self, prop, **kwargs):
        super(DatetimeField, self).__init__(prop, **kwargs)

    def to_resource(self, data):
        val = super(DatetimeField, self).to_resource(data)

        if val:
            # Make a datetime
            return coerce_to_datetime(val)
        return None

    def from_resource(self, obj, field):
        """
        Outout a datetime to str val
        """

        val = super(DatetimeField, self).from_resource(obj, field)

        if not val:
            return None

        # Make a String from datetime
        return coerce_from_datetime(val)
