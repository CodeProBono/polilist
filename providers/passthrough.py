#!/usr/bin/env python

import providers.base
import sys
import time

from util.notifier import *

try:
    import httplib2
except ImportError:
    sys.stderr.write('Failed to import httplib2 (python-httplib2). Is it installed?\n')
    sys.exit(1)

class Provider(providers.base.Provider):
    """
    This class defines a basic HTTP provider with no cacheing or other
    optimisations built in. You should only use this provider when debugging
    HTTP-related issues. If you use this provider regularly you will probably
    piss off website admins by sending an unexpected number of HTTP requests.
    That is not very polite.
    """

    def __init__(self, notifier):
        self.conn = httplib2.Http()
        self.last_request = 0
        self.notifier = notifier

    def get(self, url):
        super(Provider, self).bePolite()
        self.notifier.write('Retrieving %s...' % url, DETAILED)
        _, content = self.conn.request(url, 'GET', \
            headers={'cache-control':'no-cache'})
        self.last_request = time.time()
        return content
