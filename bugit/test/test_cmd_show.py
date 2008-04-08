from __future__ import with_statement

from nose.tools import eq_ as eq

from bugit import storage

from bugit.test import util

def test_help():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    result = util.clitest(
        args=[
            'show',
            '--help',
            ],
        cwd=tmp,
        )
    result.check_stdout("""\
Usage: bugit show [OPTS] [TICKET]

Options:
  -h, --help       show this help message and exit
  -v, --verbose    show more information
  --format=FORMAT  show output in this format
""")

def test_bad_no_default_ticket():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    result = util.clitest(
        args=[
            'show',
            ],
        cwd=tmp,
        exit_status=2,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
Usage: bugit show [OPTS] [TICKET]

bugit: error: no default ticket set
""")

def test_not_found_sha():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    result = util.clitest(
        args=[
            'show',
            '1111111111111111111111111111111111111111'
            ],
        cwd=tmp,
        exit_status=1,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit: Ticket not found: 1111111111111111111111111111111111111111
""")

def test_not_found_number():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    result = util.clitest(
        args=[
            'show',
            '#11'
            ],
        cwd=tmp,
        exit_status=1,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit: Ticket not found: #11
""")

def test_ambiguous():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(repo=tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/description',
            """\
Foo
""",
            )
        t.set(
            'd23959133fdca3611368d192bf6de4157a54d7a5/description',
            """\
Bar
""",
            )
    result = util.clitest(
        args=[
            'show',
            'd239'
            ],
        cwd=tmp,
        exit_status=1,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit: Matches more than one ticket: d239
""")

def test_not_found_name():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    result = util.clitest(
        args=[
            'show',
            'foo'
            ],
        cwd=tmp,
        exit_status=1,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit: Ticket not found: foo
""")

def test_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(repo=tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/number',
            '3431\n',
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
Oncolator segfaults on some inputs

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
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/seen/c26ce22b9cf7f95f23c9efc461422d8bfe386628',
            '',
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/seen/6f5613979900ee198042f6c3eb922d750bbfaa49',
            '',
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/not-seen/7d330ee77f44d4e9106d7ab5161e2e58b0c33bf6',
            '',
            )
    result = util.clitest(
        args=[
            'show',
            '#3431',
            ],
        cwd=tmp,
        )
    result.check_stdout("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970
number #3431
tags priority:high denial-of-service security
     reporter:jdoe@example.com
seen 6f5613979900ee198042f6c3eb922d750bbfaa49
     c26ce22b9cf7f95f23c9efc461422d8bfe386628
not-seen 7d330ee77f44d4e9106d7ab5161e2e58b0c33bf6

Oncolator segfaults on some inputs

The Oncolator service segfaults if I go to the web page,
login, choose quick oncolation from the radio buttons and
click the "Onc!" button.

I need to demo this to the Board of Directors on Monday, need a
fix quick! It crashed on me today around 9:20 am, you should be
able to find it in the server logs.

--
browser=Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6)
\tGecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)
""")

def test_minimal():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(repo=tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/description',
            """\
Oncolator segfaults on some inputs
""",
            )
    result = util.clitest(
        args=[
            'show',
            'd239',
            ],
        cwd=tmp,
        )
    result.check_stdout("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970

Oncolator segfaults on some inputs

--
""")

def test_minimal_with_number():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(repo=tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/number',
            '3431\n',
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/description',
            """\
Oncolator segfaults on some inputs
""",
            )
    result = util.clitest(
        args=[
            'show',
            '#3431',
            ],
        cwd=tmp,
        )
    result.check_stdout("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970
number #3431

Oncolator segfaults on some inputs

--
""")

def test_lookup_sha():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(repo=tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/description',
            """\
Oncolator segfaults on some inputs
""",
            )
    result = util.clitest(
        args=[
            'show',
            'd239371f3b6b61ca1076bb460e331b3edb412970',
            ],
        cwd=tmp,
        )
    result.check_stdout("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970

Oncolator segfaults on some inputs

--
""")

def test_lookup_sha_abbreviated_4():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(repo=tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/description',
            """\
Oncolator segfaults on some inputs
""",
            )
    result = util.clitest(
        args=[
            'show',
            'd239',
            ],
        cwd=tmp,
        )
    result.check_stdout("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970

Oncolator segfaults on some inputs

--
""")

def test_lookup_name():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(repo=tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/description',
            """\
Oncolator segfaults on some inputs
""",
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/name/oncolator-segfault',
            '',
            )
    result = util.clitest(
        args=[
            'show',
            'oncolator-segfault',
            ],
        cwd=tmp,
        )
    result.check_stdout("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970
name oncolator-segfault

Oncolator segfaults on some inputs

--
""")

def test_variable_short():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(repo=tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/description',
            """\
Oncolator segfaults on some inputs
""",
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/answer',
            "42\n",
            )
    result = util.clitest(
        args=[
            'show',
            'd239',
            ],
        cwd=tmp,
        )
    result.check_stdout("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970

Oncolator segfaults on some inputs

--
answer=42
""")

def test_variable_long():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(repo=tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/description',
            """\
Oncolator segfaults on some inputs
""",
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/ashortone',
            # just short enough not to wrap
            ((70 - len('something=')) * 'x') + '\n',
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/longerone',
            # just one too long
            ((71 - len('longerone=')) * 'x') + '\n',
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/toolong',
            50*'foo ',
            )
    result = util.clitest(
        args=[
            'show',
            'd239',
            ],
        cwd=tmp,
        )
    result.check_stdout("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970

Oncolator segfaults on some inputs

--
ashortone=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
longerone=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
toolong=foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo
\tfoo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo
\tfoo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo
\tfoo
""")

def test_variable_multiline():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(repo=tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/description',
            """\
Oncolator segfaults on some inputs
""",
            )
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/multiline',
            """\
I consist of
multiple lines
and my formatting
is precious and
dear to author
"""
            )
    result = util.clitest(
        args=[
            'show',
            'd239',
            ],
        cwd=tmp,
        )
    result.check_stdout("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970

Oncolator segfaults on some inputs

--
multiline=
\tI consist of
\tmultiple lines
\tand my formatting
\tis precious and
\tdear to author
""")

def test_multiple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(repo=tmp) as t:
        t.set(
            'd239371f3b6b61ca1076bb460e331b3edb412970/description',
            """\
Oncolator segfaults on some inputs
""",
            )
        t.set(
            'b6de831319bcac7de17dbd85432792daae5925dc/description',
            """\
Frob is kabork.
""",
            )
    result = util.clitest(
        args=[
            'show',
            'd239',
            'b6de831319bca',
            ],
        cwd=tmp,
        )
    result.check_stdout("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970

Oncolator segfaults on some inputs

--
---
ticket b6de831319bcac7de17dbd85432792daae5925dc

Frob is kabork.

--
""")
