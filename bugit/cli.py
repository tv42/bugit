import logging
import optparse
import sys
import pkg_resources

class MyFormatter(optparse.IndentedHelpFormatter):
    def format_epilog(self, epilog):
        return epilog

def subcommands():
    for entrypoint in \
            pkg_resources.iter_entry_points('bugit.command'):
        fn = entrypoint.load()
        yield (entrypoint.name, fn.__doc__)

class AppInfo(object):
    """Top-level program state and helper functions."""
    pass

def main():
    logging.basicConfig()

    parser = optparse.OptionParser(
        usage='%prog COMMAND [ARGS]',
        epilog=("\nCommon commands include:\n"
                + '\n'.join([
                    '  %s\t%s' % (name, blurb)
                    for (name, blurb) in sorted(subcommands())
                    ])
                + '\n'
                ),
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

    appinfo = AppInfo()

    command = args.pop(0)
    for entrypoint in \
            pkg_resources.iter_entry_points('bugit.command', command):
        fn = entrypoint.load()
        return fn(appinfo, args)

    parser.error('Unknown command: %s' % command)
