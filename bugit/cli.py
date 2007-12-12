import logging
import optparse
import sys

class MyFormatter(optparse.IndentedHelpFormatter):
    def format_epilog(self, epilog):
        return epilog

def main():
    logging.basicConfig()

    parser = optparse.OptionParser(
        usage='%prog COMMAND [ARGS]',
        #TODO generate epilog list
        epilog="""
Common commands include:
  list\tList tickets matching given criteria
  show\tShow details of a ticket
""",
        formatter=MyFormatter(),
        )
    my_options = []
    all_options = sys.argv[1:]
    while all_options and all_options[0].startswith('-'):
        my_options.append(all_options.pop(0))
    (options, args) = parser.parse_args(my_options)
    assert not args
    args = all_options

    if not args:
        parser.print_help()
        sys.exit(1)

    raise NotImplementedError
