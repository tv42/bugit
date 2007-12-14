import optparse
import os

from bugit import storage

def main(args):
    """Initialize git repository for bugit use"""
    parser = optparse.OptionParser(
        usage='%prog init',
        )
    (options, args) = parser.parse_args(args)

    if args:
        parser.error('too many arguments')

    storage.init(repo='.')
