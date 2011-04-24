#!/usr/bin/python

import providers.base
import sys
import hashlib
import os

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

    def __init__(self):
        self.conn = httplib2.Http()
        if not os.path.exists(CACHE_DIR):
            os.mkdir(CACHE_DIR)

    def get(self, url):
        cached_copy = os.path.join(CACHE_DIR, hashlib.sha1(url).hexdigest())
        content = None
        if os.path.exists(cached_copy):
            f = open(cached_copy, 'r')
            content = f.read()
            f.close()
        else:
            _, content = self.conn.request(url, 'GET')
            f = open(cached_copy, 'w')
            f.write(content)
            f.close()
        return content

    def clearCache(self):
        for page in os.listdir(CACHE_DIR):
            os.remove(os.path.join(CACHE_DIR, page))
