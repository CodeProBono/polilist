#!/usr/bin/env python

class Exporter(object):
    """
    A basic template for an exporter (class of object that writes a collection
    of people to some file or other data sink). All exporters should inherit
    from this class and also be named Exporter (for compatibility with the
    getObject function).
    """

    def __init__(self, destination, notifier):
        self.destination = destination
        self.notifier = notifier

    def write(self, people):
        """
        Exporters should override this function such that it writes the
        collection of people passed to an appropriate location.
        """
        pass
