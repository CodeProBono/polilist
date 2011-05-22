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
        r_email = re.compile('^mailto:.*')
        r_phone = re.compile('.*(Contact Details)|(To contact C)|(You can contact C)|(Phone:)|(Mobile:).*[0-9].*')
        r_letters = re.compile('[A-Za-z]')

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
                parts = re.sub('&.*?;', '', re.sub(r'<.*?>', '', \
                    str(moresoup.findAll('h1')[0]).split(\
                    '&#40;')[0]).replace('&#32;', ' ')).split()
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

            try:
                person['email'] = re.sub(r'<.*?>', '', str(\
                    moresoup.findAll('a', href=r_email)[0]))
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining email number on page %s' % \
                    (str(inst), page), DEBUG)

            try:
                for line in moresoup.findAll('p', text=r_phone):
                    ph_nums = filter(None, map(lambda x: re.sub(r'[^0-9]', \
                        '', x), r_letters.split(str(line))))
                    for num in ph_nums:
                        if len(num) == 10:
                            if num.startswith('02'):
                                person['phone'] = num
                            else:
                                person['mobile'] = num
                        elif len(num) == 8:
                            person['phone'] = '02%s' % num
                        else:
                            person['person'] = num
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while determining phone number on page %s' % \
                    (str(inst), page), DEBUG)

            person['level'] = 'local'
            person['state'] = 'NSW'
            person['electorate'] = 'Wollondilly'

            people.append(person)

        return people
