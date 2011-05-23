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

        # REs

        pages_processed = []
        people = []

        for p in soup.findAll('h2', text=re.compile('.*Councillor.*'))[9:]:
            person = {}

            try:
                elems = str(p).split('Councillor')[1].strip().split()
                person['firstname'], person['surname'] = elems[:2]
                if len(elems) > 2:
                    person['suffix'] = elems[2]
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining name on page %s' % \
                    (str(inst), url), DEBUG)

            try:
                person['ward'] = str(p.next.next.next.next)
                p = p.next.next.next.next.next.next.next.next
                if 'Ward' not in person['ward']:
                    # We accidentally grabbed the address.
                    del person['ward']
                else:
                    person['ward'] = person['ward'].replace('Ward', '').strip()
                    p = p.next
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining ward on page %s' % \
                    (str(inst), url), DEBUG)

            try:
                person['address'], person['suburb'] = map(lambda x: x.strip(), str(p).split(',')[:2])
                person['postcode'] = person['suburb'].split()[-1]
                person['suburb'] = ' '.join(person['suburb'].split()[:-1])
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining address on page %s' % \
                    (str(inst), url), DEBUG)

            try:
                p = p.next.next.next.next
                person['phone'] = re.sub(r'[^0-9]', '', str(p))
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining phone number on page %s' % \
                    (str(inst), url), DEBUG)

            try:
                p = p.next.next.next.next
                person['mobile'] = re.sub(r'[^0-9]', '', str(p))
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining mobile on page %s' % \
                    (str(inst), url), DEBUG)

            try:
                p = p.next.next.next.next
                person['fax'] = re.sub(r'[^0-9]', '', str(p))
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining fax number on page %s' % \
                    (str(inst), url), DEBUG)

            try:
                p = p.next.next.next.next.next
                person['email'] = str(p)
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining email on page %s' % \
                    (str(inst), url), DEBUG)

            person['level'] = 'local'
            person['state'] = 'NSW'
            person['electorate'] = 'Wollondilly'

            people.append(person)

        return people
