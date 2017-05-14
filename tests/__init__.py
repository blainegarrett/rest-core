"""
Test Suite for rest-core suite
"""

import unittest
import os
import sys

from google.appengine.ext import testbed

# Bootstrap the external libs
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TEST_DIR, '../external'))
sys.path.insert(0, os.path.join(TEST_DIR, '../rest_core'))
sys.path.insert(0, TEST_DIR)


class BaseCase(unittest.TestCase):
    """
    Base Unit Test Case
    """
    is_unit = True

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        self.testbed.init_datastore_v3_stub()
        self.testbed.init_taskqueue_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()

    def tearDown(self):
        self.testbed.deactivate()
        pass
