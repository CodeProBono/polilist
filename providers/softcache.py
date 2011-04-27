#!/usr/bin/python

import providers.base
import sys
import os
import time

from util.notifier import *

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
    def __init__(self, notifier):
        self.conn = httplib2.Http(CACHE_DIR)
        self.last_request = 0
        self.notifier = notifier

    def get(self, url):
        super(Provider, self).bePolite()
        self.notifier.write('Retrieving %s...' % url, DETAILED)
        _, content = self.conn.request(url, 'GET')
        self.last_request = time.time()
        return content

    def clearCache(self):
        self.notifier.write('Clearing cache...', DEBUG)
        for page in map(lambda x:os.path.join(CACHE_DIR, x), \
            os.listdir(CACHE_DIR)):
            self.notifier.write('Deleting %s...' % page)
            os.remove(page)
