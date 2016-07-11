"""
Test for custom param coersion back and forth between REST input and native representation
"""

from tests import BaseCase
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api.datastore_errors import BadValueError
import params
import datetime

test_dtstr = "1982-09-02T05:30:15Z"
test_dtobj = datetime.datetime(year=1982, month=9, day=2, hour=5, minute=30, second=15)


class CoerceToCursorTests(BaseCase):
    """ Tests for voluptuous coersion to str to ndb cursor object """

    def test_none(self):
        # Assert none case
        self.assertIsNone(params.coerce_to_cursor(None))
        self.assertIsNone(params.coerce_to_cursor(""))
        self.assertIsNone(params.coerce_to_cursor([]))

    def test_error(self):
        self.assertRaises(BadValueError, params.coerce_to_cursor, "invalid")

    def test_base(self):
        cursor_str = "CkIKGgoNbW9kaWZpZWRfZGF0ZRIJCOLF0ZHYhM0CEiBqCnN-YXJ0cy02MTJyEgsSBUV2ZW50GICAgMDUxpgKDBgAIAE="
        result = params.coerce_to_cursor(cursor_str)
        self.assertTrue(isinstance(result, Cursor))


class CoerceToDatetimeTests(BaseCase):
    """ Tests for voluptuous coersion to str to datetime object """

    def test_none(self):
        # Assert none case
        self.assertIsNone(params.coerce_to_datetime(None))

    def test_error(self):
        self.assertRaises(ValueError, params.coerce_to_datetime, "invalid")

    def test_timestamp(self):
        result = params.coerce_to_datetime(test_dtstr)
        self.assertTrue(isinstance(result, datetime.datetime))
        self.assertEqual([result.year, result.month, result.day], [1982, 9, 2])
        self.assertEqual([result.hour, result.minute, result.second], [5, 30, 15])

    def test_datestamp(self):
        result = params.coerce_to_datetime("1982-09-02")
        self.assertTrue(isinstance(result, datetime.datetime))
        self.assertEqual([result.year, result.month, result.day], [1982, 9, 2])
        self.assertEqual([result.hour, result.minute, result.second], [0, 0, 0])


class CoerceFromDatetimeTests(BaseCase):
    """ Tests for voluptuous coersion from datetime object to str for output """

    def test_none(self):
        # Assert none case
        self.assertIsNone(params.coerce_from_datetime(None))

    def test_error(self):
        self.assertRaises(AttributeError, params.coerce_from_datetime, "invalid")

    def test_base(self):
        self.assertEqual(params.coerce_from_datetime(test_dtobj), test_dtstr)
