from __future__ import with_statement

import optparse
import os
import sys

from bugit import lookup
from bugit import serialize
from bugit import storage
from bugit import util

def main(appinfo, args):
    """Show details of a ticket"""
    parser = optparse.OptionParser(
        usage='%prog show [OPTS] [TICKET]',
        )
    parser.add_option(
        '-v', '--verbose',
        help='show more information',
        action='count',
        )
    parser.add_option(
        '--format',
        help='show output in this format',
        )
    (options, args) = parser.parse_args(args)

    if options.verbose:
        raise NotImplementedError
    if options.format:
        raise NotImplementedError

    if not args:
        # TODO check for stored default ticket
        parser.error('no default ticket set')

    requested = list(args)
    with storage.Transaction(repo='.') as t:
        while True:
            requested_ticket = requested.pop(0)
            try:
                ticket = lookup.match(
                    transaction=t,
                    requested_ticket=requested_ticket,
                    )
            except lookup.TicketLookupError, e:
                print >>sys.stderr, '%s: %s' % (
                    os.path.basename(sys.argv[0]),
                    e,
                    )
                sys.exit(1)

            serialize.serialize(
                transaction=t,
                ticket=ticket,
                fp=sys.stdout,
                )

            if not requested:
                break

            print '---'
