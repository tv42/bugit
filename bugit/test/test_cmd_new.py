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
        allow_stderr=True,
        )
    result.check_stdout('')
    stderr = result.stderr.splitlines(True)
    assert len(stderr) >= 1
    m = re.match('^bugit new: creating ticket ([0-9a-f]{40}) \.\.\.$', stderr[0])
    assert m is not None, \
        'Ticket creation stderr is bad:\n%s' % result.stderr
    ticket = m.group(1)
    eq(
        stderr[1:],
        [
            "bugit new: saved\n",
            ],
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
        allow_stderr=True,
        )
    result.check_stdout('')
    stderr = result.stderr.splitlines(True)
    assert len(stderr) >= 1
    m = re.match('^bugit new: creating ticket ([0-9a-f]{40}) \.\.\.$', stderr[0])
    assert m is not None, \
        'Ticket creation stderr is bad:\n%s' % result.stderr
    ticket = m.group(1)
    eq(
        stderr[1:],
        [
            "bugit new: saved\n",
            ],
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
    stderr = result.stderr.splitlines(True)
    assert len(stderr) >= 1
    m = re.match('^bugit new: creating ticket ([0-9a-f]{40}) \.\.\.$', stderr[0])
    assert m is not None, \
        'Ticket creation stderr is bad:\n%s' % result.stderr
    ticket = m.group(1)
    eq(
        stderr[1:],
        [
            "bugit new: cannot include ticket identity when creating ticket\n",
            ],
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
        allow_stderr=True,
        )
    result.check_stdout('')
    stderr = result.stderr.splitlines(True)
    assert len(stderr) >= 1
    m = re.match('^bugit new: creating ticket ([0-9a-f]{40}) \.\.\.$', stderr[0])
    assert m is not None, \
        'Ticket creation stderr is bad:\n%s' % result.stderr
    ticket = m.group(1)
    eq(
        stderr[1:],
        [
            "bugit new: saved\n",
            ],
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

def test_editor_fail():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    orig_head = storage.git_rev_parse(
        rev='bugit/HEAD',
        repo=tmp,
        )
    class FakeTTYFileDescription(object):
        def isatty(self):
            return True

    FAKE_EDITOR = os.path.join(
        os.path.dirname(__file__),
        'editor-that-fails',
        )

    result = util.clitest(
        args=[
            'new',
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
    stderr = result.stderr.splitlines(True)
    assert len(stderr) >= 1
    m = re.match('^bugit new: creating ticket ([0-9a-f]{40}) \.\.\.$', stderr[0])
    assert m is not None, \
        'Ticket creation stderr is bad:\n%s' % result.stderr
    eq(
        stderr[1:],
        [
            "bugit new: editor failed with exit status 42\n",
            #TODO "bugit new: file was not changed, discarding\n",
            ],
        )
    new_head = storage.git_rev_parse(
        rev='bugit/HEAD',
        repo=tmp,
        )
    eq(orig_head, new_head)

def test_editor_noop():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    orig_head = storage.git_rev_parse(
        rev='bugit/HEAD',
        repo=tmp,
        )
    class FakeTTYFileDescription(object):
        def isatty(self):
            return True

    FAKE_EDITOR = os.path.join(
        os.path.dirname(__file__),
        'editor-that-does-nothing',
        )

    result = util.clitest(
        args=[
            'new',
            ],
        environ=dict(
            BUGIT_EDITOR=FAKE_EDITOR,
            ),
        stdin=FakeTTYFileDescription(),
        allow_stderr=True,
        cwd=tmp,
        )
    result.check_stdout('')
    stderr = result.stderr.splitlines(True)
    assert len(stderr) >= 1
    m = re.match('^bugit new: creating ticket ([0-9a-f]{40}) \.\.\.$', stderr[0])
    assert m is not None, \
        'Ticket creation stderr is bad:\n%s' % result.stderr
    eq(
        stderr[1:],
        [
            "bugit new: file was not changed, discarding\n",
            ],
        )
    new_head = storage.git_rev_parse(
        rev='bugit/HEAD',
        repo=tmp,
        )
    eq(orig_head, new_head)

def test_editor_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    class FakeTTYFileDescription(object):
        def isatty(self):
            return True

    FAKE_EDITOR = os.path.join(
        os.path.dirname(__file__),
        'editor-append',
        )

    result = util.clitest(
        args=[
            'new',
            ],
        environ=dict(
            BUGIT_EDITOR=FAKE_EDITOR,
            ),
        stdin=FakeTTYFileDescription(),
        allow_stderr=True,
        cwd=tmp,
        )
    result.check_stdout('')
    stderr = result.stderr.splitlines(True)
    assert len(stderr) >= 1
    m = re.match('^bugit new: creating ticket ([0-9a-f]{40}) \.\.\.$', stderr[0])
    assert m is not None, \
        'Ticket creation stderr is bad:\n%s' % result.stderr
    ticket = m.group(1)
    eq(
        stderr[1:],
        [
            "bugit new: saved\n",
            ],
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
    eq(got, [ticket])
