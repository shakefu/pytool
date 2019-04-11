import os
import sys

import six
import mock

import pytool
from .util import eq_, raises, SkipTest


class TestCommand(pytool.cmd.Command):
    def set_opts(self):
        self.opt('--test', action='store_true', help='This is my test option.')

    def run(self):
        pass


class TestSubcommand(pytool.cmd.Command):
    def parser_opts(self):
        if pytool.cmd.HAS_CAP:
            return dict(auto_env_var_prefix='test_')
        return dict()

    def set_opts(self):
        self.opt('--test', action='store_true')
        self.subcommand('action', self.action, self.run_action)

    def action(self):
        self.opt('--act', action='store_true')

    def run_action(self):
        pass

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


def test_subcommand_no_args():
    if six.PY2:
        raise SkipTest
    cmd = TestSubcommand()
    cmd.start([])
    eq_(cmd.args.test, False)
    eq_(cmd.args.command, None)


def test_subcommand_env_var_prefix():
    if six.PY2 or not pytool.cmd.HAS_CAP:
        raise SkipTest
    cmd = TestSubcommand()
    cmd.start([])
    eq_(cmd.parser._auto_env_var_prefix, 'test_')


def test_subcommand_with_arg():
    if six.PY2:
        raise SkipTest
    cmd = TestSubcommand()
    cmd.start(['--test'])
    eq_(cmd.args.test, True)
    eq_(cmd.args.command, None)


def test_subcommand_with_cmd():
    cmd = TestSubcommand()
    cmd.start(['action'])
    eq_(cmd.args.test, False)
    eq_(cmd.args.command, 'action')
    eq_(cmd.args.act, False)


def test_subcommand_with_args():
    cmd = TestSubcommand()
    cmd.start(['--test', 'action', '--act'])
    eq_(cmd.args.test, True)
    eq_(cmd.args.command, 'action')
    eq_(cmd.args.act, True)


@mock.patch('sys.exit')
def test_stop(exit):
    pytool.cmd.Command().stop()
    exit.assert_called_with(0)


@mock.patch('pytool.cmd.Command.start')
def test_console_script(start):
    TestCommand().console_script()
    start.assert_called_with(sys.argv[1:])


class test_configargparse():
    def setup(self):
        if not pytool.cmd.HAS_CAP:
            raise SkipTest

        class Cmd(pytool.cmd.Command):
            def parser_opts(self):
                return dict(auto_env_var_prefix='test_')

            def set_opts(self):
                self.opt('--test', action='store_true',
                         help='This is my test option.')
                self.opt('--config', '-c', is_config_file=True)

            def run(self):
                pass

        self.Cmd = Cmd

    @mock.patch.dict(os.environ, {'TEST_TEST': 'true'})
    def test_env_var(self):
        cmd = self.Cmd()
        cmd.start([])
        eq_(cmd.args.test, True)

    def test_conf_file(self):
        cmd = self.Cmd()
        cmd.start(['-c', 'test/test_conf.yml'])
        eq_(cmd.args.test, True)
