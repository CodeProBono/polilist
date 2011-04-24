#!/usr/bin/python

import providers.base
import sys
import os
import time

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
        self.last_request = 0

    def get(self, url):
        super(Provider, self).bePolite()
        _, content = self.conn.request(url, 'GET')
        self.last_request = time.time()
        return content

    def clearCache(self):
        for page in os.listdir(CACHE_DIR):
            os.remove(os.path.join(CACHE_DIR, page))
