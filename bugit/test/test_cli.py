from nose.tools import eq_ as eq

from bugit.test import util

USAGE = """\
Usage: bugit COMMAND [ARGS]

Options:
  -h, --help  show this help message and exit

Common commands include:
  edit\tEdit a ticket
  init\tInitialize git repository for bugit use
  list\tList tickets matching given criteria
  new\tCreate a new ticket
  show\tShow details of a ticket
"""

def test_no_args():
    result = util.clitest(
        args=[],
        exit_status=1,
        )
    result.check_stdout(USAGE)

def test_global_help():
    result = util.clitest(
        args=[
            '--help',
            ],
        )
    result.check_stdout(USAGE)

def test_bad_command():
    result = util.clitest(
        args=[
            'xyzzy',
            ],
        allow_stderr=True,
        exit_status=2,
        )
    result.check_stdout('')
    result.check_stderr("""\
Usage: bugit COMMAND [ARGS]

bugit: error: Unknown command: xyzzy
""")
