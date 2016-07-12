"""
Example Helper Utilities
"""

import os


def get_domain():
    return os.environ['HTTP_HOST']
