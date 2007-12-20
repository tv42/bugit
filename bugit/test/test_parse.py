from __future__ import with_statement

from nose.tools import eq_ as eq, assert_raises

from cStringIO import StringIO

from bugit import parse

def next(g, variable, value=''):
    got = g.next()
    (got_var, got_val) = got
    eq(got_var, variable)
    eq(got_val, value)

def test_empty():
    fp = StringIO('')
    g = parse.parse_ticket(fp)
    assert_raises(StopIteration, g.next)

def test_simple_raw():
    fp = StringIO("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970
number #3431
tags priority:high denial-of-service security
     reporter:jdoe@example.com
seen build/301

Oncolator segfaults on some inputs

The Oncolator service segfaults if I go to the web page,
login, choose quick oncolation from the radio buttons and
click the "Onc!" button.

I need to demo this to the Board of Directors on Monday, need a
fix quick! It crashed on me today around 9:20 am, you should be
able to find it in the server logs.

browser=Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6)
\tGecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)
""")
    g = parse.parse_ticket_raw(fp)
    next(g, '_ticket', 'd239371f3b6b61ca1076bb460e331b3edb412970\n')
    next(g, '_number', '#3431\n')
    next(g, '_tags', 'priority:high denial-of-service security reporter:jdoe@example.com\n')
    next(g, '_seen', 'build/301\n')
    next(g, '_description', """\
Oncolator segfaults on some inputs

The Oncolator service segfaults if I go to the web page,
login, choose quick oncolation from the radio buttons and
click the "Onc!" button.

I need to demo this to the Board of Directors on Monday, need a
fix quick! It crashed on me today around 9:20 am, you should be
able to find it in the server logs.
""")
    next(g, 'browser', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)\n')
    assert_raises(StopIteration, g.next)

def test_simple():
    fp = StringIO("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970
number #3431
tags priority:high denial-of-service security
     reporter:jdoe@example.com
seen build/301

Oncolator segfaults on some inputs

The Oncolator service segfaults if I go to the web page,
login, choose quick oncolation from the radio buttons and
click the "Onc!" button.

I need to demo this to the Board of Directors on Monday, need a
fix quick! It crashed on me today around 9:20 am, you should be
able to find it in the server logs.

browser=Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6)
\tGecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)
""")
    g = parse.parse_ticket(fp)
    next(g, '_ticket', 'd239371f3b6b61ca1076bb460e331b3edb412970\n')
    next(g, 'number', '#3431\n')
    next(g, 'tags/priority:high')
    next(g, 'tags/denial-of-service')
    next(g, 'tags/security')
    next(g, 'tags/reporter:jdoe@example.com')
    # TODO seen lookup!
    next(g, 'description', """\
Oncolator segfaults on some inputs

The Oncolator service segfaults if I go to the web page,
login, choose quick oncolation from the radio buttons and
click the "Onc!" button.

I need to demo this to the Board of Directors on Monday, need a
fix quick! It crashed on me today around 9:20 am, you should be
able to find it in the server logs.
""")
    next(g, 'browser', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)\n')
    assert_raises(StopIteration, g.next)

def test_simple_separator():
    fp = StringIO("""\
ticket d239371f3b6b61ca1076bb460e331b3edb412970
number #3431
tags priority:high denial-of-service security
     reporter:jdoe@example.com
seen build/301

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
    g = parse.parse_ticket(fp)
    next(g, '_ticket', 'd239371f3b6b61ca1076bb460e331b3edb412970\n')
    next(g, 'number', '#3431\n')
    next(g, 'tags/priority:high')
    next(g, 'tags/denial-of-service')
    next(g, 'tags/security')
    next(g, 'tags/reporter:jdoe@example.com')
    # TODO seen lookup!
    next(g, 'description', """\
Oncolator segfaults on some inputs

The Oncolator service segfaults if I go to the web page,
login, choose quick oncolation from the radio buttons and
click the "Onc!" button.

I need to demo this to the Board of Directors on Monday, need a
fix quick! It crashed on me today around 9:20 am, you should be
able to find it in the server logs.
""")
    next(g, 'browser', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)\n')
    assert_raises(StopIteration, g.next)

def test_noheader():
    fp = StringIO("""\
Oncolator segfaults on some inputs

The Oncolator service segfaults if I go to the web page,
login, choose quick oncolation from the radio buttons and
click the "Onc!" button.

I need to demo this to the Board of Directors on Monday, need a
fix quick! It crashed on me today around 9:20 am, you should be
able to find it in the server logs.
""")
    g = parse.parse_ticket(fp)
    next(g, 'description', """\
Oncolator segfaults on some inputs

The Oncolator service segfaults if I go to the web page,
login, choose quick oncolation from the radio buttons and
click the "Onc!" button.

I need to demo this to the Board of Directors on Monday, need a
fix quick! It crashed on me today around 9:20 am, you should be
able to find it in the server logs.
""")
    assert_raises(StopIteration, g.next)

def test_variablestyle():
    fp = StringIO("""\
_ticket=d239371f3b6b61ca1076bb460e331b3edb412970
number=#3431
tags/priority:high
tags/denial-of-service
tags/security
tags/reporter:jdoe@example.com
seen/7d4bb609013fd91c53660b9d28f384612cc58f26
date=2007-06-10T10:05:53+03:00
description=
\tOncolator segfaults on some inputs
\t
\tThe Oncolator service segfaults if I go to the web page,
\tlogin, choose quick oncolation from the radio buttons and
\tclick the "Onc!" button.
\t
\tI need to demo this to the Board of Directors on Monday, need
\ta fix quick! It crashed on me today around 9:20 am, you should
\tbe able to find it in the server logs.
browser=Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6)
\tGecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)
""")
    g = parse.parse_ticket(fp)
    next(g, '_ticket', 'd239371f3b6b61ca1076bb460e331b3edb412970\n')
    next(g, 'number', '#3431\n')
    next(g, 'tags/priority:high')
    next(g, 'tags/denial-of-service')
    next(g, 'tags/security')
    next(g, 'tags/reporter:jdoe@example.com')
    next(g, 'seen/7d4bb609013fd91c53660b9d28f384612cc58f26')
    next(g, 'date', '2007-06-10T10:05:53+03:00\n')
    next(g, 'description', """\
Oncolator segfaults on some inputs

The Oncolator service segfaults if I go to the web page,
login, choose quick oncolation from the radio buttons and
click the "Onc!" button.

I need to demo this to the Board of Directors on Monday, need
a fix quick! It crashed on me today around 9:20 am, you should
be able to find it in the server logs.
""")
    next(g, 'browser', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)\n')
    assert_raises(StopIteration, g.next)

def test_continuation():
    fp = StringIO("""\
one=
\tfoo
\tbar
""")
    g = parse.parse_ticket(fp)
    next(g, 'one', 'foo\nbar\n')
    assert_raises(StopIteration, g.next)

def test_nontab():
    fp = StringIO("""\
one=
  foo
  bar
two=
\tfoo
        bar
""")
    g = parse.parse_ticket(fp)
    next(g, 'one', 'foo\nbar\n')
    next(g, 'two', 'foo\nbar\n')
    assert_raises(StopIteration, g.next)

def test_nontab_leadingspace():
    fp = StringIO("""\
one=
  foo
   bar
two=
   foo
  bar
""")
    g = parse.parse_ticket(fp)
    next(g, 'one', 'foo\n bar\n')
    next(g, 'two', ' foo\nbar\n')
    assert_raises(StopIteration, g.next)

def test_continuation_emptyline_withwhitespace():
    fp = StringIO("""\
one=
\t
\tbar
""")
    g = parse.parse_ticket(fp)
    next(g, 'one', '\nbar\n')
    assert_raises(StopIteration, g.next)

def test_continuation_emptyline_nowhitespace():
    fp = StringIO("""\
one=

\tbar
""")
    g = parse.parse_ticket(fp)
    next(g, 'one', '\nbar\n')
    assert_raises(StopIteration, g.next)
