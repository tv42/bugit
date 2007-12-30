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
    eq(result.stdout, """\
Usage: bugit edit [TICKET]

Options:
  -h, --help  show this help message and exit
  --replace   replace ticket fully with input
  --update    update ticket based on input, preserving anything not included
""",
       'stdout does not match:\n%s' % result.stdout)

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
        )
    eq(
        result.stdout,
        'Edited ticket %s\n' % TICKET,
        'Ticket creation stdout is bad:\n%s' % result.stdout,
        )
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
        )
    eq(
        result.stdout,
        'Edited ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5\n',
        'Ticket creation stdout is bad:\n%s' % result.stdout,
        )
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
    eq(result.stdout, '')
    eq(result.stderr, """\
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
    eq(result.stdout, '')
    eq(result.stderr, """\
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
        )
    eq(
        result.stdout,
        'Edited ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5\n',
        'Ticket creation stdout is bad:\n%s' % result.stdout,
        )
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
        )
    eq(
        result.stdout,
        'Edited ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5\n',
        'Ticket creation stdout is bad:\n%s' % result.stdout,
        )
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
        )
    eq(
        result.stdout,
        'Edited ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5\n',
        'Ticket creation stdout is bad:\n%s' % result.stdout,
        )
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
    eq(result.stdout, '')
    eq(
        result.stderr,
        'bugit edit: ticket header not on first line\n',
        'Ticket edit stderr is bad:\n%s' % result.stderr,
        )
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
    eq(result.stdout, '')
    eq(
        result.stderr,
        'bugit edit: ticket must be given in first header or as argument\n',
        'Ticket edit stderr is bad:\n%s' % result.stderr,
        )
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
