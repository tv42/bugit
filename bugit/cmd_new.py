from __future__ import with_statement

import optparse
import os
import random
import sha
import subprocess
import sys
import textwrap

from bugit import editor
from bugit import storage
from bugit import parse
from bugit import tagsort

def _sha_fp(fp):
    s = sha.new()
    while True:
        data = fp.read(8192)
        if not data:
            break
        s.update(data)
    return s.hexdigest()

def main(appinfo, args):
    """Create a new ticket"""
    parser = optparse.OptionParser(
        usage='%prog new [REV..] [--] [VARIABLE=VALUE..]',
        )
    (options, args) = parser.parse_args(args)

    if args:
        raise NotImplementedError()

    # i though of using the sha1 of the subtree of the ticket as the
    # ticket name, but that makes e.g. two "echo|bugit new" runs
    # create conflicting tickets.. just picking a random sha seems
    # simpler and should make accidental conflicts very rare
    ticket = '%040x' % random.getrandbits(160)
    print >>sys.stderr, 'bugit new: creating ticket %s ...' % ticket

    if sys.stdin.isatty():
        filename = os.path.join(
            '.git',
            'bugit',
            'new.%s.%d.ticket' % (
                ticket,
                os.getpid(),
                ),
            )

        with file(filename, 'w+') as f:
            f.write("""\
ticket %(ticket)s

Enter description here, with a short first paragraph.

Separate variables from main description with "--".
""" % dict(
                    ticket=ticket,
                    ),
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
                '%s new: editor failed with exit status %r' % (
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
                    '%s new: file was not changed, discarding' % (
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
        content = parse.parse_ticket(sys.stdin)

    with storage.Transaction('.') as t:
        for variable, value in content:
            if variable == '_ticket':
                if value.strip() != ticket:
                    # a different message based on whether we used
                    # editor or not, just to make a bit more sense
                    if sys.stdin.isatty():
                        print >>sys.stderr, \
                            '%s new: ticket identity must not be modified' % (
                            os.path.basename(sys.argv[0]),
                            )
                    else:
                        print >>sys.stderr, \
                            '%s new: cannot include ticket identity when creating ticket' % (
                            os.path.basename(sys.argv[0]),
                            )
                    sys.exit(1)
            t.set(
                os.path.join(ticket, variable),
                value,
                )
    print >>sys.stderr, \
        '%s new: saved' % (
        os.path.basename(sys.argv[0]),
        )
