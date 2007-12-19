from __future__ import with_statement

import optparse
import os
import random
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

    # i though of using the sha1 of the subtree of the ticket as the
    # ticket name, but that makes e.g. two "echo|bugit new" runs
    # create conflicting tickets.. just picking a random sha seems
    # simpler and should make accidental conflicts very rare
    ticket = '%040x' % random.getrandbits(160)
    with storage.Transaction('.') as t:
        t.set(
            os.path.join(ticket, 'description'),
            description,
            )
    print 'Saved ticket %s' % ticket
