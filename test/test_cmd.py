import sys

import mock

import pytool
from .util import eq_, raises


class TestCommand(pytool.cmd.Command):
    def set_opts(self):
        self.opt('--test', action='store_true', help='This is my test option.')

    def run(self):
        pass


def test_command_no_args():
    cmd = TestCommand()
    cmd.start([])
    eq_(cmd.args.test, False)


def test_command_with_arg():
    cmd = TestCommand()
    cmd.start(['--test'])
    eq_(cmd.args.test, True)


@raises(NotImplementedError)
def test_not_implemented():
    pytool.cmd.Command().start([])


def test_pass_coverage():
    # This is a noop
    pytool.cmd.Command().set_opts()


@mock.patch('sys.exit')
def test_stop(exit):
    pytool.cmd.Command().stop()
    exit.assert_called_with(0)


@mock.patch('pytool.cmd.Command.start')
def test_console_script(start):
    TestCommand().console_script()
    start.assert_called_with(sys.argv[1:])


