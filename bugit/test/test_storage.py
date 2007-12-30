from __future__ import with_statement

from nose.tools import eq_ as eq

import os
import subprocess

from bugit import storage

from bugit.test import util

def test_transaction_abort():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/xyzzy',
            'mockdata\n',
            )
    class MyException(Exception):
        pass
    try:
        with storage.Transaction(tmp) as t:
            t.set(
                'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/xyzzy',
                'newvalue\n',
                )
            raise MyException()
    except MyException:
        pass
    else:
        raise RuntimeError('Expected MyException')
    got = storage.get(
        path='f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/xyzzy',
        repo=tmp,
        )
    eq(got, 'mockdata\n')

def test_transaction_nop():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        pass

def test_init():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    util.check_bugit_repository(repo=tmp)

def test_init_repeat():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    util.check_bugit_repository(repo=tmp)
    storage.init(tmp)
    util.check_bugit_repository(repo=tmp)

def test_transaction_set_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/xyzzy',
            'mockdata\n',
            )
    got = storage.get(
        path='f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/xyzzy',
        repo=tmp,
        )
    eq(got, 'mockdata\n')

def test_ls_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/xyzzy',
            'mockdata\n',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/quux',
            'mock2\n',
            )
        t.set(
            '5d6d80d51c73ea24e47f2de6f207b9de5479b6b2/quux',
            'distraction\n',
            )
    got = storage.ls(
        path='f3da69cd9eca7a69ed72a4edf2d65c84e83b0411',
        repo=tmp,
        )
    got = sorted(got)
    eq(got, sorted(['xyzzy', 'quux']))

def test_rm_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/xyzzy',
            'mockdata\n',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/quux',
            'mock2\n',
            )
        t.set(
            '5d6d80d51c73ea24e47f2de6f207b9de5479b6b2/quux',
            'distraction\n',
            )
    got = storage.ls(
        path='f3da69cd9eca7a69ed72a4edf2d65c84e83b0411',
        repo=tmp,
        )
    got = sorted(got)
    eq(got, sorted(['xyzzy', 'quux']))
    with storage.Transaction(tmp) as t:
        t.rm('f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/quux')
    got = storage.ls(
        path='f3da69cd9eca7a69ed72a4edf2d65c84e83b0411',
        repo=tmp,
        )
    got = list(got)
    eq(got, ['xyzzy'])

def test_transaction_ls_simple():
    tmp = util.maketemp()
    storage.git_init(tmp)
    storage.init(tmp)
    with storage.Transaction(tmp) as t:
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/xyzzy',
            'mockdata\n',
            )
        t.set(
            'f3da69cd9eca7a69ed72a4edf2d65c84e83b0411/quux',
            'mock2\n',
            )
        t.set(
            '5d6d80d51c73ea24e47f2de6f207b9de5479b6b2/quux',
            'distraction\n',
            )
    with storage.Transaction(tmp) as t:
        got = t.ls(
            path='f3da69cd9eca7a69ed72a4edf2d65c84e83b0411',
            )
        got = sorted(got)
        eq(got, sorted(['xyzzy', 'quux']))

