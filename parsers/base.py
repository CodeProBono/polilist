#!/usr/bin/env python

class Parser(object):
    """
    A generic template for a parser. All parsers should inherit from this class,
    be named Parser and implement the functions below.
    """

    def __init__(self, provider, notifier):
        self.provider = provider
        self.notifier = notifier

    def get(url):
        """
        A parser should override this function such that it parses the page at
        the given URL and returns a list of the contacts found on it.
        """
        return []
