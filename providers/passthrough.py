#!/usr/bin/env python

import providers.base

class Provider(providers.base.Provider):
    """
    This class is to define a basic HTTP provider with no cacheing or other
    optimisations built in. You should only use this provider when debugging
    HTTP-related issues. If you use this provider regularly you will probably
    piss off website admins by sending an unexpected number of HTTP requests.
    That is not very polite.
    """
    def __init__(self):
        pass

    def get(url):
        pass
