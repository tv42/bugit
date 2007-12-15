from __future__ import with_statement

import optparse
import os
import sys
import textwrap

from bugit import storage
from bugit import tagsort

def main(args):
    """Create a new ticket"""
    parser = optparse.OptionParser(
        usage='%prog new [REV..] [--] [VARIABLE=VALUE..]',
        )
    (options, args) = parser.parse_args(args)

    if args:
        raise NotImplementedError()

    # TODO plug in an editor
    description = sys.stdin.read()

    with storage.Transaction('.') as t:
        t.set(
            '0000000000000000000000000000000000000000/description',
            description,
            )
    print 'Saved ticket 0000000000000000000000000000000000000000'
