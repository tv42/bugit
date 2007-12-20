from __future__ import with_statement

import optparse
import os
import random
import sys
import textwrap

from bugit import storage
from bugit import parse
from bugit import tagsort

def main(args):
    """Create a new ticket"""
    parser = optparse.OptionParser(
        usage='%prog new [REV..] [--] [VARIABLE=VALUE..]',
        )
    (options, args) = parser.parse_args(args)

    if args:
        raise NotImplementedError()

    if sys.stdin.isatty():
        raise NotImplementedError('TODO plug in an editor')
    else:
        content = parse.parse_ticket(sys.stdin)

    # i though of using the sha1 of the subtree of the ticket as the
    # ticket name, but that makes e.g. two "echo|bugit new" runs
    # create conflicting tickets.. just picking a random sha seems
    # simpler and should make accidental conflicts very rare
    ticket = '%040x' % random.getrandbits(160)
    with storage.Transaction('.') as t:
        for variable, value in content:
            if variable == '_ticket':
                print >>sys.stderr, \
                    '%s new: cannot include ticket identity when creating ticket' % (
                    os.path.basename(sys.argv[0]),
                    )
                sys.exit(1)
            t.set(
                os.path.join(ticket, variable),
                value,
                )
    print 'Saved ticket %s' % ticket
