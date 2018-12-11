"""
This module contains helpers related to writing scripts and creating command
line utilities.

"""

import sys
import signal

# Handle the optional configargparse lib
try:
    import configargparse as argparse
    HAS_CAP = True
except:
    import argparse
    HAS_CAP = False

import pytool.text
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


try:
    RELOAD_SIGNAL = signal.SIGUSR1
    STOP_SIGNAL = signal.SIGTERM
except AttributeError:
    # These signal symbols don't exist on Windows
    RELOAD_SIGNAL = 10
    STOP_SIGNAL = 15


class Command(object):
    """
    Base class for creating commands that can be run easily as scripts. This
    class is designed to be used with the ``console_scripts`` entry point to
    create Python-based commands for your packages.

    .. versionadded:: 3.11.0

        If the `configargparse <https://github.com/bw2/ConfigArgParse>`_
        library is installed, Pytool will automatically use that as a drop-in
        replacement for the stdlib `argparse
        <https://docs.python.org/3/howto/argparse.html>`_ module that is used
        by default.

        You should use :meth:`parser_opts` to give additional configuration
        arguments if you want to enable `configargparse` features like
        automatically using environment variables.

    **Hello world example**::

        # hello.py
        from pytool.cmd import Command

        class HelloWorld(Command):
            def run(self):
                print "Hello World."

    The only thing that *must* be defined in the subclass is the :meth:`run`
    method, which should contain the code to launch your application, all other
    methods are optional.

    **Example setup.py**::

        # setup.py
        from setuptools import setup

        setup(
            # ...
            entry_points={
                'console_scripts':[
                    'helloworld = hello:HelloWorld.console_script',
                    ],
                },
            )

    When using an entry point script, the :class:`Command` has a special
    :meth:`console_script` method for launching the application.

    **Starting without an entry point script**::

        # hello.py [cont'd]
        if __name__ == '__main__':
            import sys
            HelloWorld().start(sys.argv[1:])

    The :meth:`start` method always requires an argument - even if it's just
    an empty list.

    **More complex example**::

        from pytool.cmd import Command

        class HelloAll(Command):
            def set_opts(self):
                self.opt('--world', default='World', help="use a different "
                        "world")
                self.opt('--verbose', '-v', action='store_true', help="use "
                        "more verbose output")

            def run(self):
                print "Hello", self.args.world

                if self.args.verbose:
                    print "Hola", self.args.world

    Whenever there are arguments for a command, they're made available for your
    use as :attr:`self.args`. This object is created by :mod:`argparse` so
    refer to that documentation for more information.

    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False,
                                              **self.parser_opts())
        self.set_opts()
        self.opt('--help', action='help', help='display this help and exit')

    def parser_opts(self):
        """ Subclasses should override this method to return a dictionary of
            additional arguments to the parser instance.

            **Example**::

                class MyCommand(Command):
                    def parser_opts(self):
                        return dict(
                                description="Manual description for cmd.",
                                auto_env_var_help=True,
                                auto_env_var_prefix=True,
                                )
        """
        return dict()

    def set_opts(self):
        """ Subclasses should override this method to configure the command
            line arguments and options.

            **Example**::

                class MyCommand(Command):
                    def set_opts(self):
                        self.opt('--verbose', '-v', action='store_true',
                                help="be more verbose")

                    def run(self):
                        if self.args.verbose:
                            print "I'm verbose."
        """
        pass

    def opt(self, *args, **kwargs):
        """ Add an option to this command. This takes the same arguments as
            :meth:`ArgumentParser.add_argument`.
        """
        self.parser.add_argument(*args, **kwargs)

    def run(self):
        """ Subclasses should override this method to start the command
            process. In other words, this is where the magic happens.
        """
        raise NotImplementedError("'run' is not implemented")

    def describe(self, description):
        """
        Describe the command in more detail. This will be displayed in addition
        to the argument help.

        This automatically strips leading indentation but does not strip all
        formatting like the ``ArgumentParser(description='')`` keyword.

        **Example**::

            class MyCommand(Command):
                def set_opts(self):
                    self.describe(\"\"\"
                        This is an example command. To use the example command,
                        run it.\"\"\")

                def run(self):
                    pass


        """
        # This has to be called from within set_opts(), when the parser exists
        if not self.parser:
            return

        description = pytool.text.wrap(description, indent='    ')
        # Update the parser object with the new description
        self.parser.description = description
        # And use the raw class so it doesn't strip our formatting
        self.parser.formatter_class = argparse.RawDescriptionHelpFormatter

    @classmethod
    def console_script(cls):
        """ Method used to start the command when launched from a distutils
            console script.
        """
        cls().start(sys.argv[1:])

    def start(self, args):
        """ Starts a command and registers single handlers. """
        self.args = self.parser.parse_args(args)
        signal_handler(RELOAD_SIGNAL, self.reload)
        signal_handler(STOP_SIGNAL, self.stop)
        self.run()

    def stop(self, *args, **kwargs):
        """
        Exits the currently running process with status `0`.

        Override this in your subclass if you wish to implement different
        SIGINT or SIGTERM handling for your process.

        """
        sys.exit(0)

    def reload(self):
        """
        Reloads `pyconfig <https://pypi.org/project/pyconfig/>`_ if it is
        available.

        Override this in your subclass if you wish to implement different
        reloading behavior.

        """
        if pyconfig:
            pyconfig.reload()
