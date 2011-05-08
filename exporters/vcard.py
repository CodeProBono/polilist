#!/usr/bin/env python

import exporters.base

import os

from util.notifier import *

class Exporter(exporters.base.Exporter):
    """
    An exporter for vCard 3.0.
    """

    def __init__(self, destination, notifier):
        if not os.path.exists(destination):
            raise Exception('Destination %s does not exist' % destination)
        if not os.path.isdir(destination):
            raise Exception('Destination %s is not a directory' % destination)
        if os.listdir(destination):
            raise Exception('Destination %s is not empty' % destination)
        self.destination = destination
        self.notifier = notifier

    def get_filename(self, attributes):
        """
        Determines a filename to write to for a given set of attributes. This
        function is used to avoid naming conflicts.
        """
        base = ""
        if 'firstname' in attributes.keys():
            base += attributes['firstname']
        if 'surname' in attributes.keys():
            base += '%s%s' (('.' if base else ''), attributes['surname'])
        if not base:
            base = 'unnamed'
        counter = 0
        while os.path.exists(os.path.join(self.destination, '%s%s%s.vcf' % \
            (base, ('.' if counter else ''), counter or ''))):
            counter += 1

        return '%s%s%s.vcf' % (base, ('.' if counter else ''), counter or '')

    def write(self, people):
        for person in people:
            filename = self.get_filename(person)
            f = open(os.path.join(self.destination, filename), 'w')
            f.write('BEGIN:VCARD\nVERSION:3.0\n')

            f.write('N:')
            if 'surname' in person.keys():
                f.write('%s;' % person['surname'])
            if 'firstname' in person.keys():
                f.write(person['firstname'])
            f.write('\n')

            f.write('FN:')
            if 'firstname' in person.keys():
                f.write('%s ' % person['firstname'])
            if 'surname' in person.keys():
                f.write(person['surname'])
            f.write('\n')

            if 'telephone' in person.keys():
                f.write('TEL:%s\n' % person['telephone'])

            if 'email' in person.keys():
                f.write('EMAIL:%s\n' % person['email'])

            # TODO: Better field matching and more vCard attributes.

            f.write('END:VCARD\n')
            f.close()

