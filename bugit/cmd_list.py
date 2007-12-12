import optparse

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

    #raise NotImplementedError('TODO')
