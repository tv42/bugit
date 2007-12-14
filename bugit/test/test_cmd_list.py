from __future__ import with_statement

from nose.tools import eq_ as eq

from bugit import storage

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

def test_empty():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    result = util.clitest(
        args=[
            'list',
            ],
        cwd=tmp,
        )
    eq(result.stdout, '')

def test_no_match():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/number',
            '3431\n',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/title',
            'I am not a xyzzy bug\n',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/tags/quux',
            '',
            )
    result = util.clitest(
        args=[
            'list',
            '--tag=xyzzy',
            ],
        cwd=tmp,
        )
    eq(result.stdout, '')

def test_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/number',
            '3431\n',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/title',
            'Oncolator segfaults on some inputs\n',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/tags/priority:high',
            '',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/tags/denial-of-service',
            '',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/tags/security',
            '',
            )
    result = util.clitest(
        args=[
            'list',
            ],
        cwd=tmp,
        )
    eq(result.stdout, """\
#3431\tOncolator segfaults on some inputs
  priority:high denial-of-service security
""")

def test_tag_wrap():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/number',
            '3431\n',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/title',
            'Oncolator segfaults on some inputs\n',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/tags/priority:high',
            '',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/tags/denial-of-service',
            '',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/tags/security',
            '',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/tags/lots-of-long-tickets',
            '',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/tags/blah-blah-blah',
            '',
            )
    result = util.clitest(
        args=[
            'list',
            ],
        cwd=tmp,
        )
    eq(result.stdout, """\
#3431\tOncolator segfaults on some inputs
  priority:high blah-blah-blah denial-of-service lots-of-long-tickets
  security
""")
