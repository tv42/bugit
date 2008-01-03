from __future__ import with_statement

from nose.tools import eq_ as eq

import os

from bugit import storage

from bugit.test import util

def test_help():
    result = util.clitest(
        args=[
            'edit',
            '--help',
            ],
        )
    result.check_stdout("""\
Usage: bugit edit [TICKET]

Options:
  -h, --help  show this help message and exit
  --replace   replace ticket fully with input
  --update    update ticket based on input, preserving anything not included
""")

def test_simple_stdin_ticketAsArg():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
    TICKET = '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'
    result = util.clitest(
        args=[
            'edit',
            TICKET,
            ],
        stdin="""\
nop

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""",
        cwd=tmp,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: updating ticket %s ...
bugit edit: saved
""" % TICKET)
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [TICKET])
    got = sorted(storage.ls(
            path=TICKET,
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                #TODO 'tags/reporter:TODO'
                ]),
        )
    got = storage.get(
        path=os.path.join(TICKET, 'description'),
        repo=tmp,
        )
    eq(got, """\
Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""")

def test_simple_stdin_ticketInStdin():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
    result = util.clitest(
        args=[
            'edit',
            ],
        stdin="""\
ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""",
        cwd=tmp,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: updating ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5 ...
bugit edit: saved
""")
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, ['29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'])
    got = sorted(storage.ls(
            path='29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                #TODO 'tags/reporter:TODO'
                ]),
        )
    got = storage.get(
        path=os.path.join(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            'description',
            ),
        repo=tmp,
        )
    eq(got, """\
Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""")

def test_simple_stdin_ticketAsBoth_ok():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
    TICKET = '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'
    result = util.clitest(
        args=[
            'edit',
            TICKET,
            ],
        stdin="""\
ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""",
        cwd=tmp,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: updating ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5 ...
bugit edit: saved
""")
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [TICKET])
    got = sorted(storage.ls(
            path=TICKET,
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                #TODO 'tags/reporter:TODO'
                ]),
        )
    got = storage.get(
        path=os.path.join(TICKET, 'description'),
        repo=tmp,
        )
    eq(got, """\
Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""")

def test_simple_stdin_ticketAsBoth_no_match():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
    TICKET = '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'
    result = util.clitest(
        args=[
            'edit',
            TICKET,
            ],
        stdin="""\
ticket aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""",
        cwd=tmp,
        exit_status=1,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: tickets on command line and in stdin do not match
""")
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [TICKET])
    got = sorted(storage.ls(
            path=TICKET,
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                #TODO 'tags/reporter:TODO'
                ]),
        )
    got = storage.get(
        path=os.path.join(TICKET, 'description'),
        repo=tmp,
        )
    eq(got, 'old')

def test_unknown_ticket_stdin():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    result = util.clitest(
        args=[
            'edit',
            ],
        stdin="""\
ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5

Frobbing is borked
""",
        cwd=tmp,
        allow_stderr=True,
        exit_status=1,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: ticket not found: 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5
""")
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [])

def test_unknown_ticket_arg():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    result = util.clitest(
        args=[
            'edit',
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            ],
        stdin="""\
nop

Frobbing is borked
""",
        cwd=tmp,
        allow_stderr=True,
        exit_status=1,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: ticket not found: 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5
""")
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [])

def test_variables():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
    result = util.clitest(
        args=[
            'edit',
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            ],
        stdin="""\
nop

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.


--
frob=v2.4
""",
        cwd=tmp,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: updating ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5 ...
bugit edit: saved
""")
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, ['29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'])
    got = sorted(storage.ls(
            path='29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                #TODO 'tags/reporter:TODO'
                'frob',
                ]),
        )
    got = storage.get(
        path=os.path.join(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            'description',
            ),
        repo=tmp,
        )
    eq(got, """\
Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""")
    got = storage.get(
        path=os.path.join(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            'frob',
            ),
        repo=tmp,
        )
    eq(got, 'v2.4\n')

def test_replace_explicit():
    # in --replace mode, all old data is wiped away! this is so that
    # if you remove a variable line from the serialized version, that
    # variable really is removed.
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/kilroy',
            'was here',
            )
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/tags/got-kilroy',
            '',
            )
    result = util.clitest(
        args=[
            'edit',
            '--replace',
            ],
        stdin="""\
ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.


--
frob=v2.4
""",
        cwd=tmp,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: replacing ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5 ...
bugit edit: saved
""")
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, ['29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'])
    got = sorted(storage.ls(
            path='29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                'frob',
                ]),
        )
    got = storage.get(
        path=os.path.join(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            'description',
            ),
        repo=tmp,
        )
    eq(got, """\
Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""")
    got = storage.get(
        path=os.path.join(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            'frob',
            ),
        repo=tmp,
        )
    eq(got, 'v2.4\n')

def test_update_explicit():
    # in --update mode, untouched data persists
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/kilroy',
            'was here\n',
            )
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/tags/got-kilroy',
            '',
            )
    result = util.clitest(
        args=[
            'edit',
            '--update',
            ],
        stdin="""\
ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.


--
frob=v2.4
""",
        cwd=tmp,
        allow_stderr=True,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: updating ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5 ...
bugit edit: saved
""")
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, ['29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'])
    got = sorted(storage.ls(
            path='29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                'kilroy',
                'tags/got-kilroy',
                'frob',
                ]),
        )
    got = storage.get(
        path=os.path.join(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            'description',
            ),
        repo=tmp,
        )
    eq(got, """\
Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""")
    got = storage.get(
        path=os.path.join(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            'kilroy',
            ),
        repo=tmp,
        )
    eq(got, 'was here\n')
    got = storage.get(
        path=os.path.join(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            'frob',
            ),
        repo=tmp,
        )
    eq(got, 'v2.4\n')

def test_ticket_not_first_arg():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
    result = util.clitest(
        args=[
            'edit',
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            ],
        stdin="""\
tags foo
ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""",
        cwd=tmp,
        allow_stderr=True,
        exit_status=1,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: updating ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5 ...
bugit edit: ticket header not on first line
""")
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, ['29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'])
    got = sorted(storage.ls(
            path='29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                #TODO 'tags/reporter:TODO'
                ]),
        )
    got = storage.get(
        path=os.path.join(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            'description',
            ),
        repo=tmp,
        )
    eq(got, 'old')

def test_ticket_not_first_no_arg():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
    result = util.clitest(
        args=[
            'edit',
            ],
        stdin="""\
tags foo
ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""",
        cwd=tmp,
        allow_stderr=True,
        exit_status=1,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: ticket must be given in first header or as argument
""")
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, ['29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'])
    got = sorted(storage.ls(
            path='29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                #TODO 'tags/reporter:TODO'
                ]),
        )
    got = storage.get(
        path=os.path.join(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5',
            'description',
            ),
        repo=tmp,
        )
    eq(got, 'old')

def test_editor_fail():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
    TICKET = '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'
    class FakeTTYFileDescription(object):
        def isatty(self):
            return True

    FAKE_EDITOR = os.path.join(
        os.path.dirname(__file__),
        'editor-that-fails',
        )

    result = util.clitest(
        args=[
            'edit',
            TICKET,
            ],
        environ=dict(
            BUGIT_EDITOR=FAKE_EDITOR,
            ),
        stdin=FakeTTYFileDescription(),
        cwd=tmp,
        allow_stderr=True,
        exit_status=1,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: editing ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5 ...
bugit edit: editor failed with exit status 42
""")
#TODO bugit edit: file was not changed, discarding
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [TICKET])
    got = sorted(storage.ls(
            path=TICKET,
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                ]),
        )
    got = storage.get(
        path=os.path.join(TICKET, 'description'),
        repo=tmp,
        )
    eq(got, 'old')

def test_editor_noop():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
    orig_head = storage.git_rev_parse(
        rev='refs/bugit/HEAD',
        repo=tmp,
        )
    TICKET = '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'
    class FakeTTYFileDescription(object):
        def isatty(self):
            return True

    FAKE_EDITOR = os.path.join(
        os.path.dirname(__file__),
        'editor-that-does-nothing',
        )

    result = util.clitest(
        args=[
            'edit',
            TICKET,
            ],
        environ=dict(
            BUGIT_EDITOR=FAKE_EDITOR,
            ),
        stdin=FakeTTYFileDescription(),
        allow_stderr=True,
        cwd=tmp,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: editing ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5 ...
bugit edit: file was not changed, discarding
""")
    new_head = storage.git_rev_parse(
        rev='refs/bugit/HEAD',
        repo=tmp,
        )
    eq(orig_head, new_head)
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [TICKET])
    got = sorted(storage.ls(
            path=TICKET,
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                ]),
        )
    got = storage.get(
        path=os.path.join(TICKET, 'description'),
        repo=tmp,
        )
    # without explicit no-edit detection, this gets a newline appended
    eq(got, 'old')

def test_editor_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/xyzzy',
            'foo',
            )
    TICKET = '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'
    class FakeTTYFileDescription(object):
        def isatty(self):
            return True

    FAKE_EDITOR = os.path.join(
        os.path.dirname(__file__),
        'editor-replace',
        )

    result = util.clitest(
        args=[
            'edit',
            TICKET,
            ],
        environ=dict(
            BUGIT_EDITOR=FAKE_EDITOR,
            ),
        stdin=FakeTTYFileDescription(),
        allow_stderr=True,
        cwd=tmp,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: editing ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5 ...
bugit edit: replacing ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5 ...
bugit edit: saved
""")
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [TICKET])
    got = sorted(storage.ls(
            path=TICKET,
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                'xyzzy',
                ]),
        )
    got = storage.get(
        path=os.path.join(TICKET, 'description'),
        repo=tmp,
        )
    # as a side-effect, description got trailing newline
    eq(got, 'old\n')
    got = storage.get(
        path=os.path.join(TICKET, 'xyzzy'),
        repo=tmp,
        )
    eq(got, 'bar\n')

def test_editor_no_ticket():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5/description',
            'old',
            )
    orig_head = storage.git_rev_parse(
        rev='refs/bugit/HEAD',
        repo=tmp,
        )
    TICKET = '29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5'
    class FakeTTYFileDescription(object):
        def isatty(self):
            return True

    FAKE_EDITOR = os.path.join(
        os.path.dirname(__file__),
        'editor-that-does-nothing',
        )

    result = util.clitest(
        args=[
            'edit',
            ],
        environ=dict(
            BUGIT_EDITOR=FAKE_EDITOR,
            ),
        stdin=FakeTTYFileDescription(),
        exit_status=1,
        allow_stderr=True,
        cwd=tmp,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit edit: Missing ticket argument for interactive editing
""")
    new_head = storage.git_rev_parse(
        rev='refs/bugit/HEAD',
        repo=tmp,
        )
    eq(orig_head, new_head)
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [TICKET])
    got = sorted(storage.ls(
            path=TICKET,
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                ]),
        )
    got = storage.get(
        path=os.path.join(TICKET, 'description'),
        repo=tmp,
        )
    # without explicit no-edit detection, this gets a newline appended
    eq(got, 'old')
