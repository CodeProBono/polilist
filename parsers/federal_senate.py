#/usr/bin/env python

import sys
import re
import os
import urlparse
import string

import parsers.base

from util.notifier import *

try:
    import BeautifulSoup
except ImportError:
    sys.stderr.write('Failed to import BeautifulSoup (python-beautifulsoup). Is it installed?\n')
    sys.exit(1)

CONTACT_LINK = '^senators\\.asp\\?id=...$'

VALID_PREFIX = ['The Hon Dr', 'The Hon', 'Dr', 'Mr', 'Mrs', 'Ms', 'the Hon']

class Parser(parsers.base.Parser):

    def get(self, url):
        """
        Parser for the federal senate.
        """
        self.notifier.write('Parsing %s...' % url, DEBUG)
        soup = BeautifulSoup.BeautifulSoup(self.provider.get(url))

        # REs
        r_electorate = re.compile('^Senator for .*')
        r_title = re.compile('^Positions?:.*')
        r_phone = re.compile('^(Phone)|(Toll Free):.*')
        r_fax = re.compile('^Fax:.*')
        r_party = re.compile('^Party:.*')
        r_address = re.compile('^Electorate Office:.*')
        r_email = re.compile('mailto:(?!web\.reps@aph\.gov\.au)')

        people = []

        for page in soup.findAll('a', href=re.compile(CONTACT_LINK)):
            self.notifier.write('Parsing %s (referenced by %s)...' % \
                (page['href'], url), DEBUG)
            moresoup = BeautifulSoup.BeautifulSoup(self.provider.get(\
                urlparse.urljoin(url, page['href'])))
            person = {}

            # Name.
            try:
                s = str(re.sub(r'<.*?>', '', str(moresoup.findAll(\
                    'h2')[0])).strip()[len('Senator '):])
                for p in VALID_PREFIX:
                    if s.startswith(p):
                        person['prefix'] = p
                        s = s[len(p):]
                        break
                person['firstname'], person['surname'] = s.split()[:2]
            except Exception as inst:
                self.notifier.writeError('%s while determining name on %s' % \
                    (str(inst), page), DEBUG)

            # Electorate.
            try:
                person['electorate'] = str(moresoup.findAll('p', \
                    text=r_electorate)[0])[len('Senator for '):]
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining electorate on %s' % (str(inst), \
                    page), DEBUG)

            # Title.
            try:
                person['title'] = str(moresoup.findAll('p', \
                    text=r_title)[0].next.next).strip()
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining title on %s' % (str(inst), \
                    page), DEBUG)

            # Phone.
            try:
                counter = 0
                for i in moresoup.findAll('p', text=r_phone):
                    person['telephone%s' % (counter or '')] = re.sub(\
                        r'[^0-9]', '', re.sub(r'<.*?>', '', str(i.next.next)))
                    if len(person['telephone%s' % (counter or '')]) > 10:
                        # Split joint phone numbers.
                        person['telephone%s' % (counter + 1)] = \
                            person['telephone%s' % (counter or '')][10:]
                        person['telephone%s' % (counter or '')] = \
                            person['telephone%s' % (counter or '')][:10]
                        counter += 1
                    counter += 1
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining phone on %s' % (str(inst), \
                    page), DEBUG)

            # Fax.
            try:
                counter = 0
                for i in moresoup.findAll('p', text=r_fax):
                    person['fax%s' % (counter or '')] = re.sub(\
                        r'[^0-9]', '', re.sub(r'<.*?>', '', str(i.next.next)))
                    counter += 1
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining fax on %s' % (str(inst), \
                    page), DEBUG)

            # Party.
            try:
                person['party'] = str(moresoup.findAll('p', \
                    text=r_party)[0].next).strip()
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining party on %s' % (str(inst), \
                    page), DEBUG)

            # Address(es).
            try:
                safelimit = 20 # 'Timeout' after 20 lines
                elem = moresoup.findAll('p', text=r_address)[0].next
                # Grab a reasonable block of lines.
                s = ""
                while safelimit:
                    s += str(elem)
                    elem = elem.next
                    safelimit -= 1
                # Strip the HTML.
                s = re.sub(r'<.*?>', '', s)
                # Cut off everything after phone number.
                s = s.split('Phone:')[0]
                # Catch the encoded spaces.
                s = s.replace('&nbsp;', ' ')
                # Clean up the rest of the mess.
                s = s.strip().replace('\t', '').replace('  ', ' ')
                s = s.split('\n\n')
                s1 = s[0]
                if len(s) > 1:
                    s2 = s[1]
                # Let's get the first address.
                person['address'] = '\n'.join(map(string.strip, s1.split(\
                    '\n'))[:-1])
                person['suburb'] = ' '.join(map(string.strip, s1.split(\
                    '\n'))[-1].split(' ')[:-2])
                person['state'], person['postcode'] = \
                    map(string.strip, s1.split('\n'))[-1].split(' ')[-2:]
                # Now the second.
                if len(s) > 1:
                    person['address1'] = s2.split('\n')[0].strip()
                    person['suburb1'] = ' '.join(s2.split('\n')[1].split(\
                        '  ')[0].split()[:-2])
                    person['state1'], person['postcode1'] = \
                        s2.split('\n')[1].split('  ')[0].split()[-2:]
                # FIXME: I'm not convinced the second address is parsed correctly.
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining address on %s' % (str(inst), \
                    page), DEBUG)

            # Email
            elem = moresoup.findAll('a', href=r_email)
            try:
                if elem:
                    person['email'] = elem[0]['href'][len('mailto:'):]
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining email on page %s' % (str(inst), \
                    page['href']), DEBUG)

            # URLs
            for (attribute, text) in [('biography', 'Biography'), \
                                      ('firstspeech', 'First speech'), \
                                      ('firstspeech', 'First Speech'), \
                                      ('homepage', 'Personal Home Page')]:
                try:
                    person['url_%s' % attribute] = urlparse.urljoin( \
                        url, moresoup.findAll('a', text=re.compile('.*%s.*' \
                        % text))[0].parent['href'])
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining %s on page %s' % \
                        (str(inst), attribute, page['href']), DEBUG)

            # General details
            person['level'] = 'federal'
            person['house'] = 'senate'

            people.append(person)

        return people

