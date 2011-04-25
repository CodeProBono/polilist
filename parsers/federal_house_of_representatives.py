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

VALID_PREFIX = ['The Hon Dr', 'The Hon', 'Dr', 'Mr', 'Mrs', 'Ms']

class Parser(parsers.base.Parser):

    def get(self, url):
        prefix = os.path.dirname(url)
        self.notifier.write('Parsing %s...' % url, DEBUG)
        soup = BeautifulSoup.BeautifulSoup(self.provider.get(url))

        people = []

        # Construct some regular expressions we'll need.
        r_electorate = re.compile('Electoral Division of .*')

        for page in soup.findAll('a', href=re.compile(CONTACT_LINK)):
            self.notifier.write('Parsing %s (referenced by %s)...' \
                % (page['href'], url), DEBUG)
            moresoup = BeautifulSoup.BeautifulSoup(self.provider.get(\
                os.path.join(prefix, page['href'])))
            person = {}

            # Electorate
            elem = moresoup.findAll('p', text=r_electorate)
            if elem:
                person['electorate'] = elem[0].strip()[len('Electoral Division of '):]

            # Name.
            elem = moresoup.findAll('h2')
            if elem:
                fullname = elem[0].string
                for p in VALID_PREFIX:
                    if fullname.startswith(p):
                        person['prefix'] = p
                        fullname = fullname[len(p):]
                        break;
                parts = fullname.split()
                if len(parts) >= 2:
                    person['firstname'] = parts[0]
                    person['surname'] = parts[1]
                    person['suffix'] = ' '.join(parts[2:])
                else:
                    self.notifier.writeError(\
                        'No name found for individual on %s' % page['href'], \
                        DEBUG)

            people.append(person)
        return people

# TODO: Finish this function

