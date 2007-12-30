from __future__ import with_statement

import optparse
import os
import re
import sys

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

    if len(args) > 1:
        parser.error('too many arguments')

    (requested_ticket,) = args

    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            children=True,
            ):
            yield basename

    def list_matching_tickets(pattern):
        g = list_tickets()
        if pattern.startswith('#'):
            for ticket in g:
                number = storage.get(os.path.join(ticket, 'number'))
                if number is not None:
                    number = number.rstrip()
                    if '#%s' % number == requested_ticket:
                        yield ticket
        else:
            for ticket in g:
                if re.match('^[0-9a-f]{4,}$', requested_ticket):
                    # looks like an abbreviated sha
                    if ticket.startswith(requested_ticket):
                        yield ticket
                else:
                    has_name = storage.get(os.path.join(ticket, 'name', pattern))
                    if has_name is not None:
                        yield ticket

    if re.match('^[0-9a-f]{40}$', requested_ticket):
        # full sha, no need to look up, just check it's there
        found = False
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path=requested_ticket,
            children=False,
            ):
            found = True
        if not found:
            print >>sys.stderr, '%s: ticket not found: %s' % (
                os.path.basename(sys.argv[0]),
                requested_ticket,
                )
            sys.exit(1)
        ticket = requested_ticket
    else:
        tickets = list(list_matching_tickets(requested_ticket))
        if not tickets:
            print >>sys.stderr, '%s: ticket not found: %s' % (
                os.path.basename(sys.argv[0]),
                requested_ticket,
                )
            sys.exit(1)
        if len(tickets) > 1:
            print >>sys.stderr, \
                '%s: matches more than one ticket: %s' % (
                os.path.basename(sys.argv[0]),
                requested_ticket,
                )
            sys.exit(1)
        (ticket,) = tickets

    with storage.Transaction('.') as t:
        serialize.serialize(
            transaction=t,
            ticket=ticket,
            fp=sys.stdout,
            )
