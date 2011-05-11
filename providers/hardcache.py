#!/usr/bin/env python

import sys
import hashlib
import os
import time

CACHE_DIR = os.path.abspath('.cache.hard')

# Some juggling to make sure project modules get imported regardless of context.
if __name__ == '__main__':
    os.chdir(os.path.dirname(sys.argv[0]))
    sys.path.append('..')

import providers.base
from util.notifier import *

try:
    import httplib2
except ImportError:
    sys.stderr.write('Failed to import httplib2 (python-httplib2). Is it installed?\n')
    sys.exit(1)

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

def main():
    """
    This function allows you to directly execute this provider to prime the
    cache with pages you know you will need to retrieve later. This is useful if
    you are doing development work without a connection to the internet. You can
    prime the cache while you are online with all the pages you will need to
    request while developing offline.
    """
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: %s URL\n' % sys.argv[0])
        sys.exit(1)

    # Assume that only developers will be calling this directly, and so want
    # debug information.
    n = Notifier(sys.stdout, sys.stderr, DEBUG)
    p = Provider(n)
    p.get(sys.argv[1])

if __name__ == '__main__':
    main()
