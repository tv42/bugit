from nose.tools import eq_ as eq

from bugit.test import util

def test_help():
    result = util.clitest(
        args=[
            'list',
            '--help',
            ],
        )
    eq(result.stdout, """\
Usage: bugit list [OPTS] [--] [SEARCH..]

Options:
  -h, --help     show this help message and exit
  -v, --verbose  show more information
  --tag=TAG      only list tickets having this tag
  --order=ORDER  sort listing according to criteria
  --hide=FIELD   hide field from listing
  --show=FIELD   show field in listing
""")

def test_no_match():
    result = util.clitest(
        args=[
            'list',
            '--tag=xyzzy',
            ],
        )
    eq(result.stdout, '')
