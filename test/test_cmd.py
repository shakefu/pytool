import os
import sys

import six
import mock
import pytest

import pytool


class Command(pytool.cmd.Command):
    def set_opts(self):
        self.opt('--test', action='store_true', help='This is my test option.')

    def run(self):
        pass


class Subcommand(pytool.cmd.Command):
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
    cmd = Command()
    cmd.start([])
    assert cmd.args.test == False


def test_command_with_arg():
    cmd = Command()
    cmd.start(['--test'])
    assert cmd.args.test == True


def test_pass_coverage():
    # This is a noop
    pytool.cmd.Command().set_opts()


def test_pass_coverage_again():
    # This is a noop
    pytool.cmd.Command().parser_opts()


@pytest.mark.skipif(six.PY2, reason="Python 3")
def test_subcommand_no_args():
    cmd = Subcommand()
    cmd.start([])
    assert cmd.args.test == False
    assert cmd.args.command == None


@pytest.mark.skipif(six.PY2 or not pytool.cmd.HAS_CAP,
                    reason="configargparse missing")
def test_subcommand_env_var_prefix():
    cmd = Subcommand()
    cmd.start([])
    assert cmd.parser._auto_env_var_prefix == 'test_'


@pytest.mark.skipif(six.PY2, reason="Python 3")
def test_subcommand_with_arg():
    cmd = Subcommand()
    cmd.start(['--test'])
    assert cmd.args.test == True
    assert cmd.args.command == None


def test_subcommand_with_cmd():
    cmd = Subcommand()
    cmd.start(['action'])
    assert cmd.args.test == False
    assert cmd.args.command == 'action'
    assert cmd.args.act == False


def test_subcommand_with_args():
    cmd = Subcommand()
    cmd.start(['--test', 'action', '--act'])
    assert cmd.args.test == True
    assert cmd.args.command == 'action'
    assert cmd.args.act == True


@mock.patch('sys.exit')
def test_stop(exit):
    pytool.cmd.Command().stop()
    exit.assert_called_with(0)


@mock.patch('pytool.cmd.Command.start')
def test_console_script(start):
    Command().console_script()
    start.assert_called_with(sys.argv[1:])


@pytest.mark.skipif(not pytool.cmd.HAS_CAP, reason="configargparse missing")
class test_configargparse():
    def setup(self):
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
        assert cmd.args.test == True

    def test_conf_file(self):
        cmd = self.Cmd()
        cmd.start(['-c', 'test/test_conf.yml'])
        assert cmd.args.test == True
