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

        people = []

        r_person = re.compile('.*Clr.*')

        for entry in soup.findAll('a', text=r_person):
            person = {}

            try:
                person['firstname'], person['surname'] = str(entry).strip( \
                    ).split()[1:3]
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining name on page %s' % (str(inst), \
                    url), DEBUG)

            try:
                entry = entry.next.next.next
                person['address'] = str(entry).strip()

                # Assume that any line not beginning with a capital is
                # a continuation of the address.
                entry = entry.next.next
                while str(entry).strip()[0] not in string.uppercase:
                    person['address'] += '\n%s' % str(entry).strip()
                    entry = entry.next.next
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining address on page %s' % (str(inst), \
                    url), DEBUG)

            try:
                person['suburb'], person['state'], person['postcode'] \
                    = map(lambda x: re.sub(r'&nbsp;', '', x), \
                    str(entry).strip().split()[:3])
                person['suburb'] = person['suburb'].capitalize()
            except Exception as inst:
                self.notifier.writeError('%s while determining suburb,' + \
                    ' state, postcode from %s on page %s' % (str(inst), \
                    str(entry), url), DEBUG)

            try:
                entry = entry.next.next
                digits = re.sub(r'[^0-9]', '', str(entry))
                person['phone'] = digits[0:8]
                if len(digits) > 8: # Assume two numbers.
                    person['phone1'] = digits[8:]
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining phone number on page %s' % \
                    (str(inst), url), DEBUG)

            try:
                while True: # Grr... where's do-while in python?
                    entry = entry.next.next
                    s = str(entry).strip()
                    if 'Fax' in s:
                        person['fax'] = re.sub(r'[^0-9]', '', s)
                    elif 'Mobile' in s:
                        person['mobile'] = re.sub(r'[^0-9]', '', s)
                    elif 'Email' in s:
                        while 'mailto:' not in str(entry):
                            entry = entry.next
                        person['email'] = re.sub(r'<.*?>', '', str(entry))
                        break
            except Exception as inst:
                self.notifier.writeError('%s while determining details' + \
                    ' from %s on page %s (next %s)' % (str(inst), \
                    str(entry), url, str(entry.next)), DEBUG)

            person['level'] = 'local'
            person['state'] = 'NSW'
            person['electorate'] = 'Yass'

            people.append(person)

        return people
