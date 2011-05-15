#!/usr/bin/env python

import sys
import os
import subprocess
import tempfile
import csv

def main():
    # Make sure we're in the project root (for caching).
    os.chdir('..')
    devnull = open(os.devnull, 'w')
    _, output = tempfile.mkstemp()

    try:
        subprocess.check_call(['./polilist', '--provider=hardcache', \
            '--include=federal house of representatives', '--output=%s' % \
            output], stdout=devnull, stderr=devnull)
        if os.path.getsize(output) < 2:
            # Make sure we did actually write to the file.
            raise Exception('File not written')
        f = open(output, 'r')
        reader = csv.reader(f)
        for row in reader:
            pass # Just parse all the rows
        f.close()
    except Exception as inst:
        sys.stderr.write(str(inst))
        sys.exit(1)
    finally:
        os.remove(output)
        devnull.close()

if __name__ == '__main__':
    main()
