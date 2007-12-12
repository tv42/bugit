import optparse

def main(args):
    """Show details of a ticket"""
    parser = optparse.OptionParser(
        usage='%prog show [OPTS] [--] [TICKET..]',
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
    parser.add_option(
        '--variable',
        help='display only this variable',
        metavar='NAME',
        action='append',
        )
    (options, args) = parser.parse_args(args)

    raise NotImplementedError
    if not args:
        parser.print_help()

