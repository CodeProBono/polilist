#!/usr/bin/env python

class Parser(object):
    """
    A generic template for a parser.
    """

    def __init__(self, provider, notifier):
        self.provider = provider
        self.notifier = notifier

    def get(url):
        """
        This function should be overridden to return a list of contacts.
        """
        return []
