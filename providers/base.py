#!/usr/bin/env python

import providers

class Provider:
    """
    A base template for providers to implement. You may consider all the
    functions in this class abstract (i.e. must be overridden in children). Any
    class implementing this interface must be named 'Provider' and must reside
    in the same directory as this file for it to be visible to the getProvider
    function.
    """
    def __init__(self):
        pass

def getProvider(module_name):
    """
    Returns a new instance of the given provider. This function is designed to
    encapsulate constructing the provider, such that neither this file nor the
    file containing main() needs to be aware of the provider name/location
    before run-time.
    """
    mod = __import__('providers.%s' % module_name, fromlist=['Provider'])
    p = mod.Provider()
    if not isinstance(p, providers.base.Provider):
        raise Exception('Provider defined by module %s is not a valid provider' % \
              module_name)
    return p
