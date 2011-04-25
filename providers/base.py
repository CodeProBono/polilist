#!/usr/bin/env python

import providers

import time

POLITE_WAIT = 1 # Seconds

class Provider(object):
    """
    A base template for providers to implement. You may consider all the
    functions in this class abstract (i.e. must be overridden in children). Any
    class implementing this interface must be named 'Provider' and must reside
    in the same directory as this file for it to be visible to the getProvider
    function.
    """

    def __init__(self, notifier):
        """
        Implement any required setup for the provider.
        """
        self.last_request = 0
        self.notifier = notifier

    def get(self, url):
        """
        Retrieve the page at the given URL.
        """
        pass

    def bePolite(self):
        """
        A utility function for waiting in between requests. This allows you to
        be kind to website admins by not hitting their servers so hard. Note
        that classes planning to use this function need to initialise the
        member last_request.
        """
        elapsed = time.time() - self.last_request
        if elapsed < POLITE_WAIT:
            time.sleep(POLITE_WAIT - elapsed)
        self.last_request = time.time()

def getProvider(module_name, notifier):
    """
    Returns a new instance of the given provider. This function is designed to
    encapsulate constructing the provider, such that neither this file nor the
    file containing main() needs to be aware of the provider name/location
    before run-time.
    """
    mod = __import__('providers.%s' % module_name, fromlist=['Provider'])
    p = mod.Provider(notifier)
    if not isinstance(p, providers.base.Provider):
        raise Exception('Provider defined by module %s is not a valid provider' % \
              module_name)
    return p
