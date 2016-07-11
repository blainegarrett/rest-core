import voluptuous
from tests import BaseCase
import resource


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
        self.assertRaises(TypeError, resource.Resource, 'cheese', fields)
        self.assertRaises(TypeError, resource.Resource, None, 'not a list')

    def test_init_no_obj(self):
        fields = ['list', 'of', 'things']

        r = resource.Resource(None, fields)

        self.assertEqual(r.obj, None)
        self.assertEqual(r.fields, fields)


class ResourceTestCaseFromDict(RestBaseCase):
    """
    Tests surrounding building a resource from a dictionary of raw data
    """

    def test_base(self):
        fields = [
            resource.RestField('name', required=True),
            resource.RestField('size', required=False),
        ]
        data = {'size': 'large', 'name': 'Bob'}

        r = resource.Resource(None, fields)
        result = r.from_dict(data)
        self.assertDictEqual(result, data)

    def test_optional_fields(self):
        """
        Test to ensure optional fields do not error are are not included in resource
        """

        fields = [
            resource.RestField('name', required=True),
            resource.RestField('size', required=False),
        ]
        data = {'name': 'Bob'}

        r = resource.Resource(None, fields)
        result = r.from_dict(data)
        self.assertDictEqual(result, data)

    def test_unexpected_fields(self):
        """
        Test To ensure that a dict with keys that are not in fields errors
        """

        data = {'color': 'orange', 'size': 'large'}
        fields = []

        r = resource.Resource(None, fields)
        self.assertRaises(resource.UnknownFieldError, r.from_dict, data)

    def test_required_fields(self):
        fields = [
            resource.RestField('name', required=True),
            resource.RestField('size', required=False),
        ]
        data = {'size': 'large'}

        r = resource.Resource(None, fields)
        self.assertRaises(resource.RequiredFieldError, r.from_dict, data)

    def test_output_only_fields(self):
        """
        Test to ensure fields that are output only error if they are in the input.

        TODO: This should throw a OutputOnlyError - see from_dict
        """

        fields = [
            resource.RestField('name', required=True),
            resource.RestField('size', required=False),
            resource.RestField('thing', output_only=True),
        ]
        data = {'size': 'large', 'thing': 'Yep'}

        r = resource.Resource(None, fields)
        self.assertRaises(resource.UnknownFieldError, r.from_dict, data)


class ResourceTestCaseToDict(RestBaseCase):
    """
    Tests surrounding converting a resource to dict to output for json, etc
    """

    def test_base(self):
        """
        """

        obj = {'name': 'Bob', 'size': 'large', 'color': 'orange'}
        fields = [
            resource.RestField('name', required=True),
            resource.RestField('size', required=False),
        ]

        r = resource.Resource(obj, fields)
        result = r.to_dict()

        # This ensures that other props on the "obj" do not get output to dict
        self.assertDictEqual(result, {'name': 'Bob', 'size': 'large', 'resource_type': 'NonDefinedClass'})


class ResourceFieldInitTests(RestBaseCase):
    """
    Tests around the generic instantiation of general RestField
    """

    def test_errors(self):
        """
        """

        self.assertRaises(resource.UnsupportedFieldProp, resource.RestField, 6)


class ResourceFieldFromResourceTests(RestBaseCase):
    """
    Tests surrounding getting a field value from a source object.
    """

    def test_against_dict(self):
        """
        """
        self.assertEqual('Bob', resource.RestField('name').from_resource({'name': 'Bob'}, 'name'))

    def test_against_obj(self):
        """
        """
        obj = TestObj()
        obj.name = 'Bob'
        self.assertEqual('Bob', resource.RestField('name').from_resource(obj, 'name'))


class ResourceFieldToResourceTests(RestBaseCase):
    """
    Tests surrounding getting a field value from a input resource.
    """

    def test_base(self):
        """
        """

        input_data = {'name': 'Bob'}
        self.assertEqual('Bob', resource.RestField('name').to_resource(input_data))

    def test_required(self):
        """
        """
        input_data = {'name': ''}

        r = resource.RestField('name', required=True)
        self.assertRaises(resource.RequiredFieldError, r.to_resource, input_data)

    def test_output_only(self):
        """
        """

        input_data = {'size': 'large', 'thing': 'Yep'}

        r = resource.RestField('thing', output_only=True)
        self.assertRaises(resource.OutputOnlyError, r.to_resource, input_data)

    def test_validation(self):
        """
        Test to ensure that our validation runs if given
        """

        input_data = {'size': 'large', 'thing': 'Yep'}

        r = resource.RestField('size', validator=voluptuous.Coerce(int))
        self.assertRaises(resource.RestValueException, r.to_resource, input_data)
        # Size cannot be coerced to an int...


class RestIntegrationTests(RestBaseCase):
    is_unit = False # Slow tests

    def simple_test(self):
        """
        """

        fields = [
            resource.RestField('sku', output_only=True),
            resource.RestField('name', required=True),
            resource.RestField('size')]

        # Create A Resource from an object - Base Test
        obj = {'name': 'Bob', 'size': 'large', 'sku': '1234'}

        r = resource.Resource(obj, fields)
        result = r.to_dict()
        self.assertDictEqual(result, {'name': 'Bob', 'size': 'large', 'sku': '1234'})

        # Create A Resource from a input dict
        input_data = {'name': 'Bob', 'size': 'large'}
        result = r.from_dict(input_data)
        self.assertDictEqual(result, {'name': 'Bob', 'size': 'large'})
