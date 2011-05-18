#!/usr/bin/env python

import sys
import re
import string

import parsers.base

from util.notifier import *

try:
    import BeautifulSoup
except ImportError:
    sys.stderr.write('Failed to import BeautifulSoup (python-beautifulsoup). Is it installed?\n')
    sys.exit(1)

class Parser(parsers.base.Parser):

    def get(self, url):
        self.notifier.write('Parsing %s...' % url, DEBUG)
        soup = BeautifulSoup.BeautifulSoup(self.provider.get(url))

        pages_processed = []
        people = []

        for page in soup.findAll('a', text=re.compile('^Cr .*')):

            # Check we haven't already seen this link.
            try:
                page = page.parent['href']
                if page in pages_processed:
                    raise Exception('Already parsed')
            except:
                continue
            pages_processed.append(page)

            moresoup = BeautifulSoup.BeautifulSoup(self.provider.get(page))

            person = {}

            # Name
            try:
                parts = re.sub('&.*?;', '', re.sub(r'<.*?>', '', str(moresoup.findAll('h1')[0]).split('&#40;')[0]).replace('&#32;', ' ')).split()
                if parts[-1] == 'Mayor':
                    if parts[-2] == 'Deputy':
                        person['firstname'], person['surname'] = parts[-4:-2]
                    else:
                        person['firstname'], person['surname'] = parts[-3:-1]
                else:
                    person['firstname'], person['surname'] = parts[-2:]
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining name number on page %s' % \
                    (str(inst), page), DEBUG)

            people.append(person)

        return people
