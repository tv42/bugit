from __future__ import with_statement

import optparse
import os
import random
import sys
import textwrap

from bugit import storage
from bugit import parse
from bugit import tagsort

def _ensure_ticket(repo, rev, ticket):
    exists = storage.git_ls_tree(
        path=ticket,
        repo=repo,
        treeish=rev,
        )
    try:
        exists.next()
    except StopIteration:
        print >>sys.stderr, '%s edit: ticket not found: %s' % (
            os.path.basename(sys.argv[0]),
            ticket,
            )
        sys.exit(1)

def main(args):
    """Edit a ticket"""
    parser = optparse.OptionParser(
        usage='%prog edit [TICKET]',
        )
    (options, args) = parser.parse_args(args)

    ticket = None
    if args:
        try:
            (ticket,) = args
        except ValueError:
            pass

    if sys.stdin.isatty():
        raise NotImplementedError('TODO plug in an editor')
    else:
        content = parse.parse_ticket(sys.stdin)

    with storage.Transaction('.') as t:
        if ticket is not None:
            _ensure_ticket(
                repo='.',
                rev=t.head,
                ticket=ticket,
                )

        for variable, value in content:
            if variable == '_ticket':
                if ticket is None:
                    ticket = value.strip()
                    _ensure_ticket(
                        repo='.',
                        rev=t.head,
                        ticket=ticket,
                        )
                else:
                    print >>sys.stderr, \
                        '%s new: cannot include ticket on both command line and stdin' % (
                        os.path.basename(sys.argv[0]),
                    )
                    sys.exit(1)
            else:
                if ticket is None:
                    print >>sys.stderr, \
                        '%s new: need to specify ticket' % (
                        os.path.basename(sys.argv[0]),
                        )
                    sys.exit(1)
                t.set(
                    os.path.join(ticket, variable),
                    value,
                    )

    assert ticket is not None
    print 'Edited ticket %s' % ticket
