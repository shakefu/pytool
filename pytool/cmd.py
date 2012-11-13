"""
This module contains helpers related to writing scripts and creating comamnd
line utilities.
"""

import sys
import signal
import argparse

try:
    import pyconfig
except ImportError:
    pyconfig = None

# Implicitly handle gevent
try:
    import gevent
except ImportError:
    signal_handler = signal.signal
else:
    signal_handler = gevent.signal


__all__ = [
        'RELOAD_SIGNAL',
        'STOP_SIGNAL',
        'Command',
        ]


RELOAD_SIGNAL = signal.SIGUSR1
STOP_SIGNAL = signal.SIGTERM


class Command(object):
    """ Base class for creating commands that can be run easily as scripts. """
    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.set_opts()
        self.opt('--help', action='help', help='display this help and exit')

    def set_opts(self):
        """ This method is to be overriden in subclasses. """
        pass

    def opt(self, *args, **kwargs):
        """ Add an option to this command. """
        self.parser.add_argument(*args, **kwargs)

    def run(self):
        """ To be overridden in subclassses. """
        raise NotImplementedError("'run' is not implemented")

    def start(self, args):
        """ Starts a command and registers single handlers. """
        self.args = self.parser.parse_args(args)
        signal_handler(RELOAD_SIGNAL, self.reload)
        signal_handler(STOP_SIGNAL, self.stop)
        self.run()

    def stop(self):
        """ Exits the currently running process. """
        sys.exit(0)

    def reload(self):
        """ Reloads the command. """
        if pyconfig:
            pyconfig.reload()


