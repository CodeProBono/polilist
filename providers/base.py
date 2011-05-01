#!/usr/bin/env python

import time

POLITE_WAIT = 1 # Seconds

class Provider(object):
    """
    A base template for providers to implement. You may consider all the
    functions in this class abstract (i.e. must be overridden in children). Any
    class implementing this interface must be named 'Provider' and must reside
    in the same directory as this file for it to be visible to the getObject
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
        that classes planning to use this function need to set self.last_request
        appropriately.
        """
        elapsed = time.time() - self.last_request
        if elapsed < POLITE_WAIT:
            time.sleep(POLITE_WAIT - elapsed)
