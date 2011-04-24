#!/usr/bin/env python

import parsers

class Parser(object):
    """
    A generic template for a parser.
    """

    def __init__(self, provider):
        self.provider = provider

    def get(url):
        """
        This function should be overridden to return a list of contacts.
        """
        return []

def getParser(module_name, provider):
    """
    Returns a new instance of the given parser.
    """
    mod = __import__('parsers.%s' % module_name, fromlist=['Parser'])
    p = mod.Parser(provider)
    if not isinstance(p, parsers.base.Parser):
        raise Exception('Parser defined by module %s is not a valid parser' % \
            module_name)
    return p
