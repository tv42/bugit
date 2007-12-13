import optparse
import os

from bugit import storage
from bugit import tagsort

def main(args):
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
        number = storage.get(os.path.join(ticket, 'number')).rstrip()
        title = storage.get(os.path.join(ticket, 'title')).rstrip()
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
        print '#%(number)s\t%(title)s' % dict(
            number=number,
            title=title,
            )
        print '  %s' % ' '.join(tags)
