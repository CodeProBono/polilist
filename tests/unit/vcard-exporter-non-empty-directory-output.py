#!/usr/bin/env python

"""
This test ensures that the vCard exporter fails during initialisation, when
passed a non-empty directory as the output location. The vCard exporter should
only operate on a non-empty directory because it produces many dynamically
named files.
"""

import tempfile
import shutil
import os
import sys

def main():
    # Create a directory we can use as the destination.
    tempdir = tempfile.mkdtemp()

    # Make the directory non-empty.
    open(os.path.join(tempdir, 'helloworld'), 'w').close()

    failure = False

    try:
        # Attempt to create the exporter.
        sys.path.append(os.path.abspath('..'))
        vcard = __import__('exporters.vcard', fromlist=['Exporter'])
        vcard.Exporter(tempdir, None)

        # If we've reached here, then the exporter did not throw an exception
        # when created, which is not what is supposed to happen.
        failure = True
    except Exception as inst:
        pass # Expected.

    shutil.rmtree(tempdir)

    if failure:
        sys.stderr.write('vCard exporter incorrectly accepted a non-empty ' + \
                         'directory as output.\n')
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
