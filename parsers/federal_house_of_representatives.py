#!/usr/bin/env python

import sys
import re
import os
import urlparse

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
        """
        Retrieves the index page of a list of contacts for the federal house of
        representatives, retrieves each contact's linked page and parses their
        details into a list of dictionaries. The parsing code itself is
        an unreadable mess, but I would argue it's difficult and unrewarding to
        write a one-shot parser in a readable manner.
        """
        self.notifier.write('Parsing %s...' % url, DEBUG)
        soup = BeautifulSoup.BeautifulSoup(self.provider.get(url))

        people = []

        # Construct some regular expressions we'll need.
        r_electorate = re.compile('Electoral Division of .*')
        r_title = re.compile('.*Title.*')
        r_party = re.compile('.*Party.*')
        r_telephone = re.compile('.*Tel:.*')
        r_fax = re.compile('.*Fax:.*')
        r_telephone_tollfree = re.compile('.*Toll Free:.*')
        r_address_parliament = re.compile('.*Parliament House Contact.*')
        r_address_office = re.compile('.*(Location)|(Postal Address).*')
        r_email = re.compile('mailto:(?!web\.reps@aph\.gov\.au)')

        for page in soup.findAll('a', href=re.compile(CONTACT_LINK)):
            self.notifier.write('Parsing %s (referenced by %s)...' \
                % (page['href'], url), DEBUG)
            moresoup = BeautifulSoup.BeautifulSoup(self.provider.get(\
                urlparse.urljoin(url, page['href'])))
            person = {}

            # Electorate
            elem = moresoup.findAll('p', text=r_electorate)
            if elem:
                person['electorate'] = \
                    elem[0].strip()[len('Electoral Division of '):]

            # Name
            elem = moresoup.findAll('h2')
            if elem:
                fullname = elem[0].string
                for p in VALID_PREFIX:
                    if fullname.startswith(p):
                        person['prefix'] = p
                        fullname = fullname[len(p):]
                        break
                parts = fullname.split()
                if len(parts) >= 2:
                    person['firstname'] = parts[0]
                    person['surname'] = parts[1]
                    person['suffix'] = ' '.join(parts[2:])
                else:
                    self.notifier.writeError(\
                        'No name found for individual on %s' % page['href'], \
                        DEBUG)
            # Title
            elem = moresoup.findAll('p', text=r_title)
            if elem:
                try:
                    elem = elem[0].next
                    person['title'] = elem.string.strip()[1:-1].strip()
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining title on page %s' % (str(inst), \
                        page['href']), DEBUG)

            # Party
            elem = moresoup.findAll('p', text=r_party)
            if elem:
                try:
                    elem = elem[0].next
                    person['party'] = elem.string.strip()[1:].strip()
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining party on page %s' % (str(inst), \
                        page['href']), DEBUG)

            # Parliament house address
            elem = moresoup.findAll('p', text=r_address_parliament)
            if elem:
                try:
                    person['address'] = '%s\n%s\n%s' % \
                        (elem[0].next.string.strip(), \
                        elem[0].next.next.next.string.strip(), \
                        elem[0].next.next.next.next.next.string.strip())
                    elem = elem[0].next.next.next.next.next.next.next.next
                    person['suburb'], person['state'], person['postcode'] = \
                        elem.string.split()[:3]
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining address on page %s' % \
                        (str(inst), page['href']), DEBUG)

            # Telephone
            elem = moresoup.findAll('p', text=r_telephone)
            counter = 0
            for s in elem:
                try:
                    person['telephone%s' % (counter or '')] = \
                        re.sub(r'[^0-9]', '', s.string.strip()[len('Tel:'):])
                    counter = counter + 1
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining phone number on page %s' % \
                        (str(inst), page['href']), DEBUG)

            # Toll free numbers
            elem = moresoup.findAll('p', text=r_telephone_tollfree)
            for s in elem:
                try:
                    person['telephone%s' % (counter or '')] = \
                        re.sub(r'[^0-9]', '', \
                        s.string.strip()[len('Toll Free:'):])
                    counter = counter + 1
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining phone number on page %s' % \
                        (str(inst), page['href']), DEBUG)
                    
            # Fax
            elem = moresoup.findAll('p', text=r_fax)
            counter = 0
            for s in elem:
                try:
                    person['fax%s' % (counter or '')] = \
                        re.sub(r'[^0-9]', '', s.string.strip()[len('Fax:'):])
                    counter = counter + 1
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining fax number on page %s' % \
                        (str(inst), page['href']), DEBUG)

            # Office address(es)
            elem = moresoup.findAll('p', text=r_address_office)
            counter = 1
            for s in elem:
                try:
                    s = s.next.next
                    person['address%s' % counter] = s.string.strip()
                    s = s.next.next
                    person['suburb%s' % counter] = \
                        ' '.join(s.string.split()[:-2])
                    person['state%s' % counter], person['postcode%s' % \
                        counter] = s.string.split()[-2:]
                    counter = counter + 1
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining address on page %s' % \
                        (str(inst), page['href']), DEBUG)

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
                                      ('homepage', 'Personal Home Page')]:
                try:
                    person['url_%s' % attribute] = urlparse.urljoin( \
                        url, moresoup.findAll('a', text=text)[0].parent['href'])
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining %s on page %s' % \
                        (str(inst), attribute, page['href']), DEBUG)

            # General details
            person['level'] = 'federal'
            person['house'] = 'house of representatives'

            people.append(person)
        return people


