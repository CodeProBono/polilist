#!/usr/bin/env python

"""
This test is designed to validate the absence of a bug where Woollahra council
contacts are returned with '<br' at the end of their surname. This bug has no
Github issue number.
"""

import sys
import os
import string

def main():
    # Imports stem from the project root.
    sys.path.append(os.path.abspath('..'))

    # Avoid polluting the working directory (and unnecessary network traffic)
    # and force the provider to use its existing cache.
    os.chdir('..')

    # Get a null handle for masking notifier output.
    nullh = open(os.devnull, 'w')

    # Construct a notifier.
    notifier = __import__('util.notifier', fromlist=['Notifier'])
    n = notifier.Notifier(nullh, nullh)

    # Construct a provider.
    hardcache = __import__('providers.hardcache', fromlist=['Provider'])
    p = hardcache.Provider(n)

    # Construct the Woollahra parser.
    woollahra = __import__('parsers.local_woollahra', fromlist=['Parser'])
    parser = woollahra.Parser(p, n)

    # Check the results of parsing for the bug.
    people = parser.get('http://www.woollahra.nsw.gov.au/council/mayor_and_councillors/profiles')
    if filter(lambda x: 'surname' in x.keys() and x['surname'].endswith(\
        '<br'), people):
        sys.stderr.write('Contacts returned with trailing <br.\n')
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
