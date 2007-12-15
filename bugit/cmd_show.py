import optparse
import os
import re
import sys
import textwrap

from bugit import storage
from bugit import tagsort
from bugit import util

def main(args):
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

    print 'ticket %s' % ticket
    number = storage.get(os.path.join(ticket, 'number'))
    if number is not None:
        number = number.rstrip()
        print 'number #%s' % number
    tags = set(storage.ls(os.path.join(ticket, 'tags')))
    if tags:
                tags = tagsort.human_friendly_tagsort(tags)
                print textwrap.fill(
                    ' '.join(tags),
                    initial_indent='tags ',
                    subsequent_indent='     ',
                    break_long_words=False,
                    )
    print 'seen build/301' #TODO
    print
    description = storage.get(os.path.join(ticket, 'description')).rstrip()
    (title, description) = util.extract_title(description)
    print '\t%s' % title
    if description is not None:
        print
        print '\n'.join([
                '\t%s' % line
                for line in description.split('\n')
                ])
    def get_the_rest():
        for name in storage.ls(ticket):
            if name in [
                'number',
                'description',
                ]:
                continue
            leading = name.split(os.sep, 1)[0]
            if leading in [
                'tags',
                'name',
                'seen',
                'not-seen',
                ]:
                continue
            yield name
    the_rest = sorted(get_the_rest())
    if the_rest:
        print
        for name in the_rest:
            content = storage.get(os.path.join(ticket, name)).rstrip()
            if not content:
                print name
            elif '\n' not in content:
                # one line with optional newline
                oneline = '%s=%s' % (name, content)
                if len(oneline) <= 70:
                    # short enough to fit on one line
                    print oneline
                else:
                    print '%s=' % name
                    print '\n'.join(textwrap.wrap(
                        content,
                        initial_indent='\t',
                        subsequent_indent='\t',
                        break_long_words=False,
                        ))
            else:
                print '%s=' % name
                print '\n'.join([
                        '\t%s' % line
                        for line in content.split('\n')
                        ])
