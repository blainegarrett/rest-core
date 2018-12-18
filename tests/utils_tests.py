"""
Test for REST helpers
"""
import mock
from tests import BaseCase
import utils


class RestUtilsBaseCase(BaseCase):
    pass


class WhiteListTests(BaseCase):
    """
    Tests Surrounding Whitelist Validation
    """

    def test_is_origin_in_whitelist(self):
        # Error Cases
        self.assertFalse(utils.is_origin_in_whitelist(None))

        # Direct Hit
        self.assertFalse(utils.is_origin_in_whitelist('http://google.com'))
        self.assertTrue(utils.is_origin_in_whitelist('http://www.example.com'))

        # Rules
        self.assertTrue(utils.is_origin_in_whitelist('http://someversion.example.appspot.com'))
        self.assertTrue(utils.is_origin_in_whitelist('http://localhost:9090'))
        self.assertFalse(utils.is_origin_in_whitelist('http://version.project.appspot.com'))
        self.assertFalse(utils.is_origin_in_whitelist('https://version-dcotx-project.appspot.com'))


class CreateRequestKeyTests(BaseCase):
    """
    Tests around the py side of creating request keys
    """

    # Note: Still trying to figure out if these are platform dependent...

    def test_sorting(self):

        # Start with a standard flat url params dict
        d1 = {u"category_slug": "exhibition-reviews",
              u"limit": "2",
              u"author_resource_id": "VXNlch4fNTc4NTkwNTA2MzI2NDI1Ng"}
        stamp1 = utils.create_request_key('test', d1)
        self.assertEqual(stamp1, 'test_4c30dcc5d73a8b1201429ea0e9cbaaaf')

        # Changing the order that the key/val pairs appear in the dict
        d2 = {u"limit": "2",
              u"author_resource_id": "VXNlch4fNTc4NTkwNTA2MzI2NDI1Ng",
              u"category_slug": "exhibition-reviews"}

        stamp2 = utils.create_request_key('test', d2)
        self.assertEqual(stamp2, 'test_4c30dcc5d73a8b1201429ea0e9cbaaaf')


@mock.patch('utils.path_to_reference')
class ApplyMiddlewareTests(BaseCase):
    """
    Tests Around Applying Middleware
    """
    @mock.patch('utils.settings.REST_MIDDLEWARE_CLASSES', None)
    def test_none(self, mock_import):
        utils.apply_middleware(None, 'some_func')
        self.assertFalse(mock_import.called)

    @mock.patch('utils.settings.REST_MIDDLEWARE_CLASSES', [])
    def test_empty(self, mock_import):
        utils.apply_middleware(None, 'some_func')
        self.assertFalse(mock_import.called)

    @mock.patch('utils.settings.REST_MIDDLEWARE_CLASSES', ['someClass'])
    def test_mocked_calls(self, mock_import):
        # Setup Mocks
        class1 = mock.Mock()
        mock_request = mock.Mock()
        mock_import.return_value = class1

        # Run Code to Test
        utils.apply_middleware(mock_request, 'some_func')

        # Check mocks
        mock_import.assert_called_once_with('someClass')
        class1.some_func.assert_called_once_with(mock_request)


    @mock.patch('utils.settings.REST_MIDDLEWARE_CLASSES', ['someClass', 'otherClass'])
    def test_mocked_multi_class(self, mock_import):
        # Setup Mocks
        class1 = mock.Mock()
        mock_request = mock.Mock()
        mock_import.return_value = class1

        # Run Code to Test
        utils.apply_middleware(mock_request, 'some_func')

        # Check mocks
        self.assertEqual(mock_import.call_count, 2)
        self.assertEqual(class1.some_func.call_count, 2)
