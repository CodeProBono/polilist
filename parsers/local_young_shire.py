#!/usr/bin/env python

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
        """
        Retrieves the councillors list from Young Shire. The state of this
        parser is a complete mess because there's very little standardisation
        on the Young Shire site and the page is in UTF-8. Most of the chaos you
        see below is an attempt to cope with edge cases.
        """
        self.notifier.write('Parsing %s...' % url, DEBUG)
        soup = BeautifulSoup.BeautifulSoup(self.provider.get(url))

        people = []

        for cell in soup.findAll('td', width="414"):
            try:
                ind = 0
                person = {}

                content = str(cell).encode('utf-8').split('\n')

                try:
                    if content[ind].strip() == '<td valign="top" width="414">':
                        # The content's wrapped onto the next line.
                        ind += 1
                    elif 'height="78"' in content[ind]:
                        # John Laybutt has his cell's height set.
                        content[ind] = content[ind][len(\
                            '<td valign="top" width="414" height="78">'):]
                    else:
                        content[ind] = content[ind][len(\
                            '<td valign="top" width="414">'):]
                    person['firstname'], person['surname'] = \
                        content[ind].strip()[len(\
                        '<font face="Arial" size="2" color="#000000"><b>'):].split(\
                        '<')[0].split()[-2:]

                    # John Walker has brackets around his name for some reason.
                    person['firstname'] = re.sub(r'[\(\)]', '', person['firstname'])
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining contact name from data %s' % \
                        (str(inst), content[ind]), DEBUG)
                    raise inst
                ind += 1

                try:
                    person['address'] = re.sub(r'<.*?>', '', content[ind]).strip()
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining contact address' % str(inst), DEBUG)
                    raise inst
                ind += 1

                if 'YOUNG' not in content[ind]:
                    # Assume we have a second address line
                    try:
                        person['address'] += '\n%s' % \
                            content[ind].split('<')[0].strip()
                    except Exception as inst:
                        self.notifier.writeError(\
                            '%s while determining second line of contact address' % \
                            str(inst), DEBUG)
                        raise inst
                    ind += 1

                # Fix HTML quotes.
                person['address'] = person['address'].replace('&quot;', '"')

                try:
                    person['suburb'], person['state'], person['postcode'] = \
                        map(string.strip, re.split(r'[.,]', re.sub(r'<.*?>', '', \
                        content[ind])))
                except Exception as inst:
                    self.notifier.writeError(\
                        '%s while determining suburb, state, postcode from data %s' \
                        % (str(inst), content[ind]), DEBUG)
                    raise inst

                ind += 1
                # And the rest...
                for line in content[ind:]:
                    # Strip the HTML tags; don't need them now.
                    line = re.sub(r'<.*?>', '', line)
                    if 'phone' in line or 'Phone' in line:
                        person['phone'] = re.sub(r'[^0-9]', '', line)
                    elif 'Mob' in line:
                        person['mobile'] = re.sub(r'[^0-9]', '', line)
                    elif re.search(r'[0-9]{4} [0-9]{4}', line):
                        # Catch phone numbers that have been wrapped.
                        person['phone%s' % ('1' if 'phone' in person.keys() else \
                            '')] = re.sub(r'[^0-9]', '', line)
                    # Wipe any null values we just accidentally added.
                    for k in ['phone', 'phone1', 'mobile']:
                        if k in person.keys() and not person[k]:
                            del person[k]

                people.append(person)
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while parsing contact %s on page %s' % (str(inst), \
                    str(cell), url), DEBUG)

        return people
