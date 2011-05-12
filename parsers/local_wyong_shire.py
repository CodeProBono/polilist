#!/usr/bin/env python

import re
import urlparse

import parsers.base
from util.notifier import *

try:
    import BeautifulSoup
except ImportError:
    sys.stderr.write('Failed to import BeautifulSoup (python-beautifulsoup). Is it installed?\n')
    sys.exit(1)

class Parser(parsers.base.Parser):

    def get(self, url):
        """
        A parser for Wyong Shire local council.
        """
        self.notifier.write('Parsing %s...' % url, DEBUG)
        soup = BeautifulSoup.BeautifulSoup(self.provider.get(url))

        people = []

        # REs we'll need
        r_phone = re.compile('^Ph: .*')
        r_email = re.compile('.*@wyong\.nsw\.gov\.au$')

        for page in soup.findAll('a', text=re.compile('^Councillor .*')):
            page = urlparse.urljoin('http://www.wyong.nsw.gov.au', \
                page.parent['href'])
            moresoup = BeautifulSoup.BeautifulSoup(self.provider.get(page))
            person = {}

            try:
                print moresoup.findAll('h1')
                person['firstname'], person['surname'] = \
                    str(moresoup.findAll('h1')[0]).split()[1:3]
                person['surname'] = re.sub(r'<.*?>', '', person['surname'])
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining name on %s' % (str(inst), \
                    page), DEBUG)

            try:
                person['phone'] = re.sub(r'[^0-9]', '', \
                    str(moresoup.findAll('p', text=r_phone)[0]))
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining phone on %s' % (str(inst), \
                    page), DEBUG)

            try:
                person['email'] = str(moresoup.findAll('a', \
                    text=r_email)[0])
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining email on %s' % (str(inst), \
                    page), DEBUG)

            person['electorate'] = 'Wyong Shire'
            person['level'] = 'local'
            person['state'] = 'NSW'

            people.append(person)
        return people

