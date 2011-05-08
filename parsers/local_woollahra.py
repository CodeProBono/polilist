#!/usr/bin/env python

import sys
import re

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
        Retrieves the councillors index page of Woollahra Council and parses
        the linked pages for each ward to get the councillors' details.
        """
        self.notifier.write('Parsing %s...\n' % url, DEBUG)
        soup = BeautifulSoup.BeautifulSoup(self.provider.get(url))

        pages_processed = []
        people = []

        # Regular expressions we'll need.
        r_ward = re.compile('.*Ward$')
        r_phone = re.compile('.*Phone: .*')
        r_fax = re.compile('.*Fax: .*')
        r_email = re.compile('.*@woollahra\.nsw\.gov\.au.*')

        for link in soup.findAll('a', text=r_ward):

            # All ward links seem to appear twice for some reason, so nix the
            # second copy.
            if link.parent['href'] in pages_processed:
                continue

            pages_processed.append(link.parent['href'])
            moresoup = BeautifulSoup.BeautifulSoup(self.provider.get(\
                link.parent['href']))

            for i in range(len(moresoup.findAll('h3'))):
                # For each councillor on the page.
                try:
                    person = {}
                    person['ward'] = str(link)
                    person['firstname'], person['surname'] = str(\
                        moresoup.findAll('h3')[i]).split(\
                        '</a>')[1][len('Councillor '):-len('</h3>')].split()[:2]

                    # Account for odd HTML artifacts.
                    if person['surname'].endswith('<br'):
                        person['surname'] = person['surname'][:-len('<br')]
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining name on page %s' % \
                        (str(inst), link.parent['href']), DEBUG)

                try:
                    person['phone'] = re.sub('[^0-9]', '', str(\
                        moresoup.findAll('p', text=r_phone)[i])[len(\
                        'Phone: '):])
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining phone number on page %s' % \
                        (str(inst), link.parent['href']), DEBUG)

                try:
                    person['fax'] = re.sub('[^0-9]', '', \
                        str(moresoup.findAll('p', text=r_fax)[i]))
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining fax number on page %s' % \
                        (str(inst), link.parent['href']), DEBUG)

                try:
                    person['email'] = str(moresoup.findAll('a', \
                        text=r_email)[i])
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining email on page %s' % \
                        (str(inst), link.parent['href']), DEBUG)

                # Common attributes.
                person['level'] = 'local'
                person['electorate'] = 'Woollahra'
                person['state'] = 'NSW'

                people.append(person)

        return people

