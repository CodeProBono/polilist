#!/usr/bin/env python

class Exporter(object):
    def __init__(self, destination, notifier):
        self.destination = destination
        self.notifier = notifier

    def write(self, people):
        pass
