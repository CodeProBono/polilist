#!/usr/bin/env python

# Verbosity levels.
NOTHING, INFORMATION, DETAILED, DEBUG = range(4)

class Notifier(object):
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
