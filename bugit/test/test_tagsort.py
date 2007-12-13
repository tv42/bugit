from nose.tools import eq_ as eq

from bugit import tagsort

def test_alphabetical():
    got = tagsort.human_friendly_tagsort(
        ['quux', 'xyzzy', 'bar', 'foo'])
    eq(got, ['bar', 'foo', 'quux', 'xyzzy'])

def test_priority_first():
    got = tagsort.human_friendly_tagsort(
        ['quux', 'priority:foo', 'bar', 'foo'])
    eq(got, ['priority:foo', 'bar', 'foo', 'quux'])

def test_unknown_semicolons_last():
    got = tagsort.human_friendly_tagsort(
        ['quux', 'froop:foo', 'bar', 'foo'])
    eq(got, ['bar', 'foo', 'quux', 'froop:foo'])
