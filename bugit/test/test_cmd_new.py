from __future__ import with_statement

from nose.tools import eq_ as eq

import os
import re

from bugit import storage

from bugit.test import util

def test_help():
    result = util.clitest(
        args=[
            'new',
            '--help',
            ],
        )
    result.check_stdout("""\
Usage: bugit new [REV..] [--] [VARIABLE=VALUE..]

Options:
  -h, --help  show this help message and exit
""")

def test_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    result = util.clitest(
        args=[
            'new',
            ],
        stdin="""\
nop

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""",
        cwd=tmp,
        )
    assert result.stdout != ''
    assert result.stdout.endswith('\n')
    assert '\n' not in result.stdout[:-1]
    m = re.match('^Saved ticket ([0-9a-f]{40})$', result.stdout)
    assert m is not None, \
        'Ticket creation stdout is bad:\n%s' % result.stdout
    ticket = m.group(1)
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [ticket])
    got = sorted(storage.ls(
            path=ticket,
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
        path=os.path.join(ticket, 'description'),
        repo=tmp,
        )
    eq(got, """\
Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""")

def test_header():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    result = util.clitest(
        args=[
            'new',
            ],
        stdin="""\
tags qwark

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""",
        cwd=tmp,
        )
    assert result.stdout != ''
    assert result.stdout.endswith('\n')
    assert '\n' not in result.stdout[:-1]
    m = re.match('^Saved ticket ([0-9a-f]{40})$', result.stdout)
    assert m is not None, \
        'Ticket creation stdout is bad:\n%s' % result.stdout
    ticket = m.group(1)
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [ticket])
    got = sorted(storage.ls(
            path=ticket,
            repo=tmp,
            ))
    eq(
        got,
        sorted([
                'description',
                #TODO 'tags/reporter:TODO'
                'tags/qwark',
                ]),
        )
    got = storage.get(
        path=os.path.join(ticket, 'description'),
        repo=tmp,
        )
    eq(got, """\
Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""")
    got = storage.get(
        path=os.path.join(ticket, 'tags/qwark'),
        repo=tmp,
        )
    eq(got, '')

def test_header_bad_ticket():
    # can't include ticket sha for "bugit new"
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    result = util.clitest(
        args=[
            'new',
            ],
        stdin="""\
ticket 29d7ae1a7d7cefd4c79d095ac0e47636aa02d4a5
tags qwark

Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""",
        cwd=tmp,
        allow_stderr=True,
        exit_status=1,
        )
    result.check_stdout('')
    result.check_stderr("""\
bugit new: cannot include ticket identity when creating ticket
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
    result = util.clitest(
        args=[
            'new',
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
    assert result.stdout != ''
    assert result.stdout.endswith('\n')
    assert '\n' not in result.stdout[:-1]
    m = re.match('^Saved ticket ([0-9a-f]{40})$', result.stdout)
    assert m is not None, \
        'Ticket creation stdout is bad:\n%s' % result.stdout
    ticket = m.group(1)
    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            repo=tmp,
            children=True,
            ):
            yield basename
    got = list(list_tickets())
    eq(got, [ticket])
    got = sorted(storage.ls(
            path=ticket,
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
        path=os.path.join(ticket, 'description'),
        repo=tmp,
        )
    eq(got, """\
Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
""")
    got = storage.get(
        path=os.path.join(ticket, 'frob'),
        repo=tmp,
        )
    eq(got, 'v2.4\n')
