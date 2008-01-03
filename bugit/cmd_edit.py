from __future__ import with_statement

import itertools
import optparse
import os
import random
import sha
import subprocess
import sys
import textwrap

from bugit import storage
from bugit import parse
from bugit import editor
from bugit import serialize
from bugit import lookup

def _sha_fp(fp):
    s = sha.new()
    while True:
        data = fp.read(8192)
        if not data:
            break
        s.update(data)
    return s.hexdigest()

def main(appinfo, args):
    """Edit a ticket"""
    parser = optparse.OptionParser(
        usage='%prog edit [TICKET]',
        )
    parser.add_option(
        '--replace',
        help='replace ticket fully with input',
        action='store_true',
        dest='replace',
        )
    parser.add_option(
        '--update',
        help='update ticket based on input, preserving anything not included',
        action='store_false',
        dest='replace',
        )
    (options, args) = parser.parse_args(args)

    ticket = None
    if args:
        try:
            (ticket,) = args
        except ValueError:
            pass

    replace = options.replace

    with storage.Transaction('.') as transaction:

        if ticket is not None:
            try:
                ticket = lookup.match(
                    transaction=transaction,
                    requested_ticket=ticket,
                    )
            except lookup.TicketLookupError, e:
                print >>sys.stderr, '%s edit: %s' % (
                    os.path.basename(sys.argv[0]),
                    e,
                    )
                sys.exit(1)

        if sys.stdin.isatty():
            if ticket is None:
                print >>sys.stderr, \
                    '%s edit: Missing ticket argument for interactive editing' % (
                    os.path.basename(sys.argv[0]),
                        )
                sys.exit(1)

            print >>sys.stderr, 'bugit edit: editing ticket %s ...' % ticket
            if replace is None:
                replace = True
            filename = os.path.join(
                '.git',
                'bugit',
                'edit.%s.%d.ticket' % (
                    ticket,
                    os.getpid(),
                    ),
                )

            with file(filename, 'w+') as f:
                serialize.serialize(
                    transaction=transaction,
                    ticket=ticket,
                    fp=f,
                    )
                f.seek(0)
                sha_before = _sha_fp(f)

            try:
                editor.run(
                    appinfo=appinfo,
                    filename=filename,
                    )
            except subprocess.CalledProcessError, e:
                print >>sys.stderr, \
                    '%s edit: editor failed with exit status %r' % (
                    os.path.basename(sys.argv[0]),
                    e.returncode,
                    )
                sys.exit(1)
            # now read back the file contents

            # non-optimal but who cares right now
            with file(filename) as f:
                sha_after = _sha_fp(f)
                if sha_before == sha_after:
                    print >>sys.stderr, \
                        '%s edit: file was not changed, discarding' % (
                        os.path.basename(sys.argv[0]),
                        )
                    sys.exit(0)

            def parse_file(filename):
                with file(filename) as f:
                    for x in parse.parse_ticket(f):
                        yield x
                os.unlink(filename)
            content = parse_file(filename)

            # TODO leaves temp file lying around on errors, generators
            # make fixing that annoying

            # TODO abort if no semantic change? get rid of sha1 check
        else:
            if replace is None:
                replace = False
            content = parse.parse_ticket(sys.stdin)

        try:
            (first_variable, first_value) = content.next()
        except StopIteration:
            raise RuntimeError('TODO')
        if first_variable == '_ticket':
            if ticket is not None:
                if first_value.strip() != ticket:
                    print >>sys.stderr, \
                        '%s edit: tickets on command line and in stdin do not match' % (
                        os.path.basename(sys.argv[0]),
                        )
                    sys.exit(1)
            else:
                ticket = first_value.strip()
        else:
            # oops, none of my business.. put it back
            content = itertools.chain([(first_variable, first_value)], content)

        if not sys.stdin.isatty():
            # batch mode
            if ticket is None:
                print >>sys.stderr, \
                    '%s edit: ticket must be given in first header or as argument' % (
                    os.path.basename(sys.argv[0]),
                        )
                sys.exit(1)

            if not lookup.exists(
                transaction=transaction,
                ticket=ticket,
                ):
                print >>sys.stderr, '%s edit: ticket not found: %s' % (
                    os.path.basename(sys.argv[0]),
                    ticket,
                    )
                sys.exit(1)

        if replace:
            action = 'replacing'
        else:
            action = 'updating'
        print >>sys.stderr, 'bugit edit: %s ticket %s ...' % (action, ticket)

        if replace:
            # ugly
            for path in transaction.ls(ticket):
                transaction.rm(os.path.join(ticket, path))

        for variable, value in content:
            if variable == '_ticket':
                print >>sys.stderr, \
                    '%s edit: ticket header not on first line' % (
                    os.path.basename(sys.argv[0]),
                    )
                sys.exit(1)
            else:
                transaction.set(
                    os.path.join(ticket, variable),
                    value,
                    )

    assert ticket is not None
    print >>sys.stderr, 'bugit edit: saved'
