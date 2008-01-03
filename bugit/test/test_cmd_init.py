from __future__ import with_statement

from nose.tools import eq_ as eq

from bugit import storage

from bugit.test import util

def test_help():
    result = util.clitest(
        args=[
            'init',
            '--help',
            ],
        )
    result.check_stdout("""\
Usage: bugit init

Options:
  -h, --help  show this help message and exit
""")

def test_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    result = util.clitest(
        args=[
            'init',
            ],
        cwd=tmp,
        )
    result.check_stdout('')
    util.check_bugit_repository(repo=tmp)

def test_repeat():
    tmp = util.maketemp()
    storage.git_init(tmp)
    result = util.clitest(
        args=[
            'init',
            ],
        cwd=tmp,
        )
    result.check_stdout('')
    util.check_bugit_repository(repo=tmp)
    result = util.clitest(
        args=[
            'init',
            ],
        cwd=tmp,
        )
    result.check_stdout('')
    util.check_bugit_repository(repo=tmp)


def test_bad_too_many_args():
    result = util.clitest(
        args=[
            'init',
            'foo',
            ],
        exit_status=2,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
Usage: bugit init

bugit: error: too many arguments
""")
