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
    eq(result.stdout, """\
Usage: bugit init

Options:
  -h, --help  show this help message and exit
""",
       'stdout does not match:\n%s' % result.stdout)

def test_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    result = util.clitest(
        args=[
            'init',
            ],
        cwd=tmp,
        )
    eq(result.stdout, '')
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
    eq(result.stdout, '')
    util.check_bugit_repository(repo=tmp)
    result = util.clitest(
        args=[
            'init',
            ],
        cwd=tmp,
        )
    eq(result.stdout, '')
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
    eq(result.stdout, '')
    eq(result.stderr, """\
Usage: bugit init

bugit: error: too many arguments
""")
