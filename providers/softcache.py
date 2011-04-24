#!/usr/bin/python

import providers.base
import sys

try:
    import httplib2
except ImportError:
    sys.stderr.write('Failed to import httplib2 (python-httplib2). Is it installed?\n')
    sys.exit(1)

CACHE_DIR = '.cache.soft'

class Provider(providers.base.Provider):
    """
    This class defines a basic HTTP provider with cacheing. It should be used
    as the provider for normal operation.
    """
    def __init__(self):
        self.conn = httplib2.Http(CACHE_DIR)

    def get(self, url):
        _, content = self.conn.request(url, 'GET')
        return content
