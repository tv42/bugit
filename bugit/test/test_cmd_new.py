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
    eq(result.stdout, """\
Usage: bugit new [REV..] [--] [VARIABLE=VALUE..]

Options:
  -h, --help  show this help message and exit
""",
       'stdout does not match:\n%s' % result.stdout)

def test_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    DESCRIPTION = """\
Frobbing is borked

I ran frob and it was supposed to blarb, but it qwarked.
"""
    result = util.clitest(
        args=[
            'new',
            ],
        stdin=DESCRIPTION,
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
    eq(got, DESCRIPTION)
