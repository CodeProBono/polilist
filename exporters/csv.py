#!/usr/bin/env python

import exporters.base

from util.notifier import *

class Exporter(exporters.base.Exporter):
    def __init__(self, destination, notifier):
        self.destination = destination
        self.notifier = notifier
        self.fd = None
        self.columns = []

    def write(self, people):
        # TODO: Cope with sensitive characters.
        # First lets figure out the columns we need.
        if not self.columns:
            self.notifier.write('Determining CSV column headings...', DEBUG)
            columns_set = set()
            for person in people:
                columns_set = columns_set.union(person.keys())
            self.columns = list(columns_set)

        if not self.fd:
            # This is the first data we've written to the output file.
            self.notifier.write('Opening destination %s...' \
                % self.destination, DEBUG)
            self.fd = open(self.destination, 'w')
            self.fd.write('%s\n' % ','.join(self.columns))

        for person in people:
            fields = []
            for col in self.columns:
                if col in person:
                    fields.append(person[col])
                else:
                    fields.append('')
            self.notifier.write('Writing record %s...' % ','.join(fields), \
                DEBUG)
            self.fd.write('%s\n' % ','.join(fields))

    def __del__(self):
        if self.fd:
            try:
                self.notifier.write('Closing %s...' % self.destination, DEBUG)
                self.fd.close()
            except:
                self.notifier.write('Closing %s failed.'% self.destination, \
                    DEBUG)
