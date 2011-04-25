#!/usr/bin/env python

import sys
import re
import os
import parsers.base

from util.notifier import *

try:
    import BeautifulSoup
except ImportError:
    sys.stderr.write('Failed to import BeautifulSoup (python-beautifulsoup). Is it installed?\n')
    sys.exit(1)

CONTACT_LINK = '^member\\.asp\\?id=...$'

class Parser(parsers.base.Parser):

    def get(self, url):
        prefix = os.path.dirname(url)
        self.notifier.write('Parsing %s...' % url, DEBUG)
        soup = BeautifulSoup.BeautifulSoup(self.provider.get(url))
        for page in soup.findAll('a', href=re.compile(CONTACT_LINK)):
            self.notifier.write('Parsing %s (referenced by %s)...' \
                % (page['href'], url), DEBUG)
            moresoup = BeautifulSoup.BeautifulSoup(self.provider.get(\
                os.path.join(prefix, page['href'])))
# TODO: Finish this function

