#!/usr/bin/env python

import providers.base
import sys
import hashlib
import os
import time

from util.notifier import *

try:
    import httplib2
except ImportError:
    sys.stderr.write('Failed to import httplib2 (python-httplib2). Is it installed?\n')
    sys.exit(1)

CACHE_DIR = '.cache.hard'

class Provider(providers.base.Provider):
    """
    This class defines a basic HTTP provider with a more agressive cache than
    the softcache provider. It assumes that a cached copy, if it exists, is
    always up to date. This provider should be used when developing so as to
    avoid repeated HTTP requests.
    """

    def __init__(self, notifier):
        self.last_request = 0
        self.conn = httplib2.Http()
        if not os.path.exists(CACHE_DIR):
            os.mkdir(CACHE_DIR)
        self.notifier = notifier

    def get(self, url):
        # Determine where this page would have been cached.
        cached_copy = os.path.join(CACHE_DIR, hashlib.sha1(url).hexdigest())
        content = None
        if os.path.exists(cached_copy):
            # The page is already in the cache.
            self.notifier.write('Retrieving %s (cached at %s)...' \
                % (url, cached_copy), DETAILED)
            f = open(cached_copy, 'r')
            content = f.read()
            f.close()
        else:
            # The page needs to be loaded into the cache.
            super(Provider, self).bePolite()
            self.notifier.write('Retrieving %s (uncached)...' % url, DETAILED)
            _, content = self.conn.request(url, 'GET')
            f = open(cached_copy, 'w')
            f.write(content)
            f.close()
            self.last_request = time.time()
        return content

    def clearCache(self):
        self.notifier.write('Clearing cache...', DEBUG)
        for page in map(lambda x:os.path.join(CACHE_DIR, x), \
            os.listdir(CACHE_DIR)):
            self.notifier.write('Deleting %s...' % page)
            os.remove(page)
