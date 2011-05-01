#!/usr/bin/env python

import string

import providers.base
import parsers.base
import exporters.base

# Verbosity levels.
NOTHING, INFORMATION, DETAILED, DEBUG = range(4)

class Notifier(object):
    """
    A class for printing notifications to the user. This encapsulation allows
    you to easily redirect notifications to a file and to adjust the level of
    verbosity of messages printed.
    """

    def __init__(self, stdout, stderr, level=INFORMATION):
        self.stdout = stdout
        self.stderr = stderr
        self.level = level

    def write(self, message, level):
        if self.level >= level:
            self.stdout.write(message + '\n')

    def writeError(self, message, level):
        if self.level >= level:
            self.stderr.write(message + '\n')

def getObject(category, module_name, notifier, **kwargs):
    """
    Creates and returns an object of the given category and module_name. This
    function abstracts the need to know the type of object that we need before
    run-time. The advantage of this is that the type of provider/parser/etc
    can be switched on the command line, causing other objects to never even be
    imported, let alone constructed.

    This abstraction allows you to write very specific objects that rely on a
    certain configuration or component availability that may not be present on
    a particular end user's system. E.g. You can write a SQLite exporter which
    will not cause problems for users who do not have SQLite installed unless
    they explicitly try to use it.

    FIXME: This function doesn't really belong here.
    """
    mod = __import__('%ss.%s' % (category, module_name), fromlist=[ \
        category.capitalize()])
    obj, base = None, None
    if category == 'provider':
        obj = mod.Provider(notifier)
        base = providers.base.Provider
    elif category == 'parser':
        obj = mod.Parser(kwargs['provider'], notifier)
        base = parsers.base.Parser
    elif category == 'exporter':
        obj = mod.Exporter(kwargs['destination'], notifier)
        base = exporters.base.Exporter
    if not isinstance(obj, base):
        raise Exception('%s defined by module %s is not a valid %s' % \
            (category.capitalize(), module_name, category))
    return obj
