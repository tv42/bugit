import optparse
import os
import textwrap

from bugit import storage
from bugit import tagsort
from bugit import util

def main(appinfo, args):
    """List tickets matching given criteria"""
    parser = optparse.OptionParser(
        usage='%prog list [OPTS] [--] [SEARCH..]',
        )
    parser.add_option(
        '-v', '--verbose',
        help='show more information',
        action='count',
        )
    parser.add_option(
        '--tag',
        help='only list tickets having this tag',
        action='append',
        )
    parser.add_option(
        '--order',
        help='sort listing according to criteria',
        )
    parser.add_option(
        '--hide',
        metavar='FIELD',
        help='hide field from listing',
        )
    parser.add_option(
        '--show',
        metavar='FIELD',
        help='show field in listing',
        )
    (options, args) = parser.parse_args(args)

    if args:
        raise NotImplementedError(
            'TODO Full text search not supported yet.')

    def list_tickets():
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            children=True,
            ):
            yield basename

    for ticket in list_tickets():
        number = storage.get(os.path.join(ticket, 'number'))
        if number is not None:
            number = number.rstrip()
            ident = '#%s' % number
        else:
            ident = ticket[:7]
        description = storage.get(os.path.join(ticket, 'description')).rstrip()
        tags = set(storage.ls(os.path.join(ticket, 'tags')))
        if options.tag:
            must = frozenset(options.tag)
            if not tags & must:
                continue
        tags = tagsort.human_friendly_tagsort(tags)
        if options.verbose:
            raise NotImplementedError
        if options.order:
            raise NotImplementedError
        if options.show:
            raise NotImplementedError
        if options.hide:
            raise NotImplementedError
        (title, description) = util.extract_title(description)
        print '%(ident)s\t%(title)s' % dict(
            ident=ident,
            title=title,
            )
        if description is not None:
            print textwrap.fill(
                ' '.join(tags),
                initial_indent='  ',
                subsequent_indent='  ',
                break_long_words=False,
                )
