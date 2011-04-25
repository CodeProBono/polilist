#!/usr/bin/env python

import exporters

class Exporter(object):
    def __init__(self, destination, notifier):
        self.destination = destination
        self.notifier = notifier

    def write(self, people):
        pass

def getExporter(module_name, destination, notifier):
    mod = __import__('exporters.%s' % module_name, fromlist=['Exporter'])
    e = mod.Exporter(destination, notifier)
    if not isinstance(e, exporters.base.Exporter):
        raise Exception('Exporter defined by module %s is not a valid exporter' % \
              module_name)
    return e
