import optparse
import os
import textwrap

from bugit import storage
from bugit import tagsort

def main(args):
    """Show details of a ticket"""
    parser = optparse.OptionParser(
        usage='%prog show [OPTS] [--] [TICKET]',
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

    # TODO fetch by sha
    assert requested_ticket.startswith('#')

    def list_tickets():
        # TODO share me
        for (mode, type_, object, basename) in storage.git_ls_tree(
            path='',
            children=True,
            ):
            yield basename

    for ticket in list_tickets():
        # TODO fetch by name

        number = storage.get(os.path.join(ticket, 'number')).rstrip()
        if '#%s' % number == requested_ticket:
            print 'ticket %s' % ticket
            print 'number #%s' % number
            tags = set(storage.ls(os.path.join(ticket, 'tags')))
            tags = tagsort.human_friendly_tagsort(tags)
            print textwrap.fill(
                ' '.join(tags),
                initial_indent='tags ',
                subsequent_indent='     ',
                break_long_words=False,
                )
            print 'seen build/301' #TODO
            print
            title = storage.get(os.path.join(ticket, 'title')).rstrip()
            print '\t%s' % title
            print
            description = storage.get(os.path.join(ticket, 'description')).rstrip()
            if description is not None:
                print '\n'.join([
                        '\t%s' % line
                        for line in description.split('\n')
                        ])
            print
            def get_the_rest():
                for name in storage.ls(ticket):
                    if name in [
                        'number',
                        'title',
                        'description',
                        ]:
                        continue
                    leading = name.split(os.sep, 1)[0]
                    if leading in [
                        'tags',
                        'seen',
                        'not-seen',
                        ]:
                        continue
                    yield name
            the_rest = sorted(get_the_rest())
            if the_rest:
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
