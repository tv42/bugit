from nose.tools import eq_ as eq

from bugit.test import util

def test_help():
    result = util.clitest(
        args=[
            'show',
            '--help',
            ],
        )
    eq(result.stdout, """\
Usage: bugit show [OPTS] [--] [TICKET..]

Options:
  -h, --help       show this help message and exit
  -v, --verbose    show more information
  --format=FORMAT  show output in this format
  --variable=NAME  display only this variable
""")
