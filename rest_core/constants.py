# Constants and defaults

# TODO: These are specific to mplsart dev obviously - in a real world app import these from proj
API_DEFAULT_ORIGIN = 'http://mplsart.com'
API_WHITELIST_DOMAINS = ['http://mplsart.com',
                         'http://www.mplsart.com',
                         'http://www.digibodies.com',
                         'http://digibodies.com',
                         'http://192.168.1.143:8080']

API_WHITELIST_RULES = [r'http://.*\.arts-612\.appspot\.com',
                       r'https://.*\-arts-612\.appspot\.com',
                       r'http://localhost:.*']
