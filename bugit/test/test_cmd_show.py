from __future__ import with_statement

from nose.tools import eq_ as eq

from bugit import storage

from bugit.test import util

def test_help():
    result = util.clitest(
        args=[
            'show',
            '--help',
            ],
        )
    eq(result.stdout, """\
Usage: bugit show [OPTS] [--] [TICKET]

Options:
  -h, --help       show this help message and exit
  -v, --verbose    show more information
  --format=FORMAT  show output in this format
""")

def test_bad_no_default_ticket():
    result = util.clitest(
        args=[
            'show',
            ],
        exit_status=2,
        allow_stderr=True,
        )
    eq(result.stdout, '')
    eq(result.stderr, """\
Usage: bugit show [OPTS] [--] [TICKET]

bugit: error: no default ticket set
""")

def test_bad_too_many_args():
    result = util.clitest(
        args=[
            'show',
            'foo',
            'bar',
            ],
        exit_status=2,
        allow_stderr=True,
        )
    eq(result.stdout, '')
    eq(result.stderr, """\
Usage: bugit show [OPTS] [--] [TICKET]

bugit: error: too many arguments
""")

def test_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/number',
            '3431\n',
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/title',
            'Oncolator segfaults on some inputs\n',
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/tags/priority:high',
            '',
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/tags/denial-of-service',
            '',
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/tags/security',
            '',
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/tags/reporter:jdoe@example.com',
            '',
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/description',
            """\
The Oncolator service segfaults if I go to the web page,
login, choose quick oncolation from the radio buttons and
click the "Onc!" button.

I need to demo this to the Board of Directors on Monday, need a
fix quick! It crashed on me today around 9:20 am, you should be
able to find it in the server logs.
""",
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/browser',
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)",
            )
    result = util.clitest(
        args=[
            'show',
            '#3431',
            ],
        cwd=tmp,
        )
    eq(result.stdout, """\
ticket d239371f3b6b61ca1076bb460e331b3edb412970
number #3431
tags priority:high denial-of-service security
     reporter:jdoe@example.com
seen build/301

\tOncolator segfaults on some inputs

\tThe Oncolator service segfaults if I go to the web page,
\tlogin, choose quick oncolation from the radio buttons and
\tclick the "Onc!" button.
\t
\tI need to demo this to the Board of Directors on Monday, need a
\tfix quick! It crashed on me today around 9:20 am, you should be
\table to find it in the server logs.

browser=
\tMozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201
\tFirefox/2.0.0.6 (Ubuntu-feisty)
""",
       'stdout does not match:\n%s' % result.stdout)
