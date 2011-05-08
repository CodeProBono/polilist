#!/usr/bin/env python

import parsers.base
from util.notifier import *

class Parser(parsers.base.Parser):
    """
    A parser for the NSW state parliament spreadsheet. This class could use the
    python CSV library, but it's a little awkward to make CSV readers accept
    strings (as opposed to file handles) and cope nicely with newlines. This
    class could easily be reused to parse any sufficiently simple CSV so, if
    required, it should be renamed to something more general.
    """

    def get(self, url):
        """
        Retrieves the contacts spreadsheet at the given url and parses it into
        a dictionary.
        """
        self.notifier.write('Parsing %s...' % url, DEBUG)
        spreadsheet = self.provider.get(url)

        # Chop the string into CSV fields and headers.
        records = spreadsheet.split('\n')
        fields = records[0].split(',')
        records = map(lambda x: x.split(','), records[1:])

        people = []

        for record in records:
            try:
                person = dict(zip(fields, record))
                # Yeah, that just happened.

                # Common attributes.
                person['level'] = 'state'
                person['electorate'] = 'NSW'

                people.append(person)
            except Exception as inst:
                self.notifier.writeError(\
                    '%s while parsing record %s in document %s' \
                    % (str(inst), record, url), DEBUG)

        return people

