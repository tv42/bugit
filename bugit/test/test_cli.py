from nose.tools import eq_ as eq

from bugit import cli

from bugit.test import util

USAGE = """\
Usage: bugit COMMAND [ARGS]

Options:
  -h, --help  show this help message and exit

Common commands include:
  list	List tickets matching given criteria
  show	Show details of a ticket
"""

def test_no_args():
    result = util.clitest(
        args=[],
        exit_status=1,
        )
    eq(result.stdout, USAGE)

def test_global_help():
    result = util.clitest(
        args=[
            '--help',
            ],
        )
    eq(result.stdout, USAGE)
