import voluptuous
from tests import BaseCase
from core import models

import resources


class TestObj(object):
    """
    An object to test resource fetching against
    """


class RestBaseCase(BaseCase):
    """
    Base Test Case for Resource
    """


class ResourceTestCase(RestBaseCase):
    """
    Tests surrounding resource
    """

    def test_errors(self):
        fields = ['list', 'of', 'things']

        # "Strings are not valid object for Resources"
        self.assertRaises(TypeError, resources.Resource, 'cheese', fields)
        self.assertRaises(TypeError, resources.Resource, None, 'not a list')

    def test_init_no_obj(self):
        fields = ['list', 'of', 'things']

        r = resources.Resource(None, fields)

        self.assertEqual(r.obj, None)
        self.assertEqual(r.fields, fields)


class ResourceTestCaseFromDict(RestBaseCase):
    """
    Tests surrounding building a resource from a dictionary of raw data
    """

    def test_base(self):
        fields = [
            resources.RestField('name', required=True),
            resources.RestField('size', required=False),
        ]
        data = {'size': 'large', 'name': 'Bob'}

        r = resources.Resource(None, fields)
        result = r.from_dict(data)
        self.assertDictEqual(result, data)

    def test_optional_fields(self):
        """
        Test to ensure optional fields do not error are are not included in resource
        """

        fields = [
            resources.RestField('name', required=True),
            resources.RestField('size', required=False),
        ]
        data = {'name': 'Bob'}

        r = resources.Resource(None, fields)
        result = r.from_dict(data)
        self.assertDictEqual(result, data)

    def test_unexpected_fields(self):
        """
        Test To ensure that a dict with keys that are not in fields errors
        """

        data = {'color': 'orange', 'size': 'large'}
        fields = []

        r = resources.Resource(None, fields)
        self.assertRaises(resources.UnknownFieldError, r.from_dict, data)

    def test_required_fields(self):
        fields = [
            resources.RestField('name', required=True),
            resources.RestField('size', required=False),
        ]
        data = {'size': 'large'}

        r = resources.Resource(None, fields)
        self.assertRaises(resources.RequiredFieldError, r.from_dict, data)

    def test_verbose_only_fields(self):
        """
        Test to ensure fields that are output only error if they are in the input.

        TODO: This should throw a OutputOnlyError - see from_dict
        """

        fields = [
            resources.RestField('name', required=True),
            resources.RestField('size', required=False),
            resources.RestField('thing', verbose_only=True),
        ]

        # Hydrate the resource
        data = {'size': 'large', 'thing': 'Yep', 'name': 'TestName'}
        r = resources.Resource(data, fields)

        # Check output
        self.assertFalse('thing' in r.to_dict())
        self.assertTrue('thing' in r.to_dict(verbose=True))

    def test_output_only_fields(self):
        """
        Test to ensure fields that are output only error if they are in the input.

        TODO: This should throw a OutputOnlyError - see from_dict
        """

        fields = [
            resources.RestField('name', required=True),
            resources.RestField('size', required=False),
            resources.RestField('thing', output_only=True),
        ]
        data = {'size': 'large', 'thing': 'Yep'}

        r = resources.Resource(None, fields)
        self.assertRaises(resources.UnknownFieldError, r.from_dict, data)


class ResourceTestCaseToDict(RestBaseCase):
    """
    Tests surrounding converting a resource to dict to output for json, etc
    """

    def test_extra_data_skipped(self):
        # Test to ensure that if a resource is given an unknown data prop, we skip it
        obj = {'name': 'Bob', 'size': 'large', 'color': 'orange'}
        fields = [
            resources.RestField('name', required=True),
            resources.RestField('size', required=False),
        ]

        r = resources.Resource(obj, fields)
        result = r.to_dict()

        # This ensures that other props on the "obj" do not get output to dict

        # Test with verbose=False
        self.assertDictEqual(result, {'name': 'Bob',
                                      'size': 'large',
                                      '_meta': {'is_verbose': True,
                                                'resource_type': 'NonDefinedClass'}})

    def test_no_verbose_fields(self):
        # Test to ensure that we properly set output meta info

        obj = {'name': 'Bob', 'size': 'large'}
        fields = [
            resources.RestField('name', required=True),
            resources.RestField('size', required=False),
        ]

        r = resources.Resource(obj, fields)
        result = r.to_dict()

        # This ensures that other props on the "obj" do not get output to dict

        # Test with verbose=False
        self.assertDictEqual(result, {'name': 'Bob',
                                      'size': 'large',
                                      '_meta': {'is_verbose': True,
                                                'resource_type': 'NonDefinedClass'}})

        # Test with verbose=True
        result = r.to_dict(verbose=True)
        self.assertDictEqual(result, {'name': 'Bob',
                                      'size': 'large',
                                      '_meta': {'is_verbose': True,
                                                'resource_type': 'NonDefinedClass'}})

    def test_with_verbose_fields(self):
        # Test to ensure that we properly set output meta info when there are verbose fields

        obj = {'name': 'Bob', 'size': 'large'}
        fields = [
            resources.RestField('name', required=True),
            resources.RestField('size', required=False, verbose_only=True),
        ]

        r = resources.Resource(obj, fields)

        # Test with verbose = True
        result = r.to_dict(verbose=True)
        self.assertDictEqual(result, {'name': 'Bob',
                                      'size': 'large',
                                      '_meta': {'is_verbose': True,
                                                'resource_type': 'NonDefinedClass'}})

        # Test with verbose = True
        result = r.to_dict(verbose=False)
        self.assertDictEqual(result, {'name': 'Bob',
                                      '_meta': {'is_verbose': False,
                                                'resource_type': 'NonDefinedClass'}})


class ResourceFieldInitTests(RestBaseCase):
    """
    Tests around the generic instantiation of general RestField
    """

    def test_errors(self):
        """
        """

        self.assertRaises(resources.UnsupportedFieldProp, resources.RestField, 6)


class ResourceFieldFromResourceTests(RestBaseCase):
    """
    Tests surrounding getting a field value from a source object.
    """

    def test_against_dict(self):
        """
        """
        self.assertEqual('Bob', resources.RestField('name').from_resource({'name': 'Bob'}, 'name'))

    def test_against_obj(self):
        """
        """
        obj = TestObj()
        obj.name = 'Bob'
        self.assertEqual('Bob', resources.RestField('name').from_resource(obj, 'name'))


class ResourceFieldToResourceTests(RestBaseCase):
    """
    Tests surrounding getting a field value from a input resources.
    """

    def test_base(self):
        """
        """

        input_data = {'name': 'Bob'}
        self.assertEqual('Bob', resources.RestField('name').to_resource(input_data))

    def test_required(self):
        """
        """
        input_data = {'name': ''}

        r = resources.RestField('name', required=True)
        self.assertRaises(resources.RequiredFieldError, r.to_resource, input_data)

    def test_output_only(self):
        """
        """

        input_data = {'size': 'large', 'thing': 'Yep'}

        r = resources.RestField('thing', output_only=True)
        self.assertRaises(resources.OutputOnlyError, r.to_resource, input_data)

    def test_validation(self):
        """
        Test to ensure that our validation runs if given
        """

        input_data = {'size': 'large', 'thing': 'Yep'}

        r = resources.RestField('size', validator=voluptuous.Coerce(int))
        self.assertRaises(resources.RestValueException, r.to_resource, input_data)
        # Size cannot be coerced to an int...


class TestModel(models.Model):
    name = models.StringProperty()
    title = models.StringProperty()
    child_resource_ids = models.StringProperty(repeated=True)
    total = models.FloatProperty()
    data = models.JsonProperty()
    start_date = models.DateTimeProperty()
    is_alive = models.BooleanProperty()
    is_available = models.BooleanProperty(default=True)


class ResourceModelTests(RestBaseCase):
    """
    Tests surrounding using core models
    """

    def test_base(self):
        FIELDS = [
            resources.ResourceIdField(output_only=True),  # TODO: This should only be on meta?
            resources.RestField(TestModel.name, required=True),
            resources.RestField(TestModel.title, required=True),
        ]

        model = TestModel()
        model.id = 'asdf'
        model.name = 'Bob'
        model.title = 'President'

        r = resources.Resource(model, FIELDS).to_dict(verbose=True)
        self.assertDictEqual(r, {'_meta': {'is_verbose': True, 'resource_type': 'TestModel'}, 'title': 'President', 'name': 'Bob', 'resource_id': 'asdf'})


class RestIntegrationTests(RestBaseCase):
    is_unit = False  # Slow tests

    def simple_test(self):
        """
        TODO: This probably doesn't need to be an integration test
        """

        fields = [
            resources.RestField('sku', output_only=True),
            resources.RestField('name', required=True),
            resources.RestField('size')]

        # Create a Resource from an object - Base Test
        obj = {'name': 'Bob', 'size': 'large', 'sku': '1234'}

        r = resources.Resource(obj, fields)
        result = r.to_dict()

        self.assertDictEqual(result, {'sku': '1234', 'name': 'Bob', 'size': 'large',
                                      '_meta': {'is_verbose': True,
                                                'resource_type': 'NonDefinedClass'}, })
        # Create a Resource from a input dict
        input_data = {'name': 'Bob', 'size': 'large'}
        result = r.from_dict(input_data)

        self.assertDictEqual(result, {'name': 'Bob', 'size': 'large'})
