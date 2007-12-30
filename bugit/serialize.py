import os
import textwrap

from bugit import tagsort

def serialize(
    transaction,
    ticket,
    fp,
    ):
    print >>fp, 'ticket %s' % ticket
    number = transaction.get(os.path.join(ticket, 'number'))
    if number is not None:
        number = number.rstrip()
        print >>fp, 'number #%s' % number
    names = sorted(transaction.ls(os.path.join(ticket, 'name')))
    if names:
        print >>fp, textwrap.fill(
            ' '.join(names),
            initial_indent='name ',
            subsequent_indent='     ',
            break_long_words=False,
            )
    tags = set(transaction.ls(os.path.join(ticket, 'tags')))
    if tags:
        tags = tagsort.human_friendly_tagsort(tags)
        print >>fp, textwrap.fill(
            ' '.join(tags),
            initial_indent='tags ',
            subsequent_indent='     ',
            break_long_words=False,
            )
    print >>fp, 'seen build/301' #TODO
    print >>fp
    description = transaction.get(os.path.join(ticket, 'description')).rstrip()
    if description:
        print >>fp, description
        print >>fp
    print >>fp, '--'
    def get_the_rest():
        for name in transaction.ls(ticket):
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
        for name in the_rest:
            content = transaction.get(os.path.join(ticket, name)).rstrip()
            if not content:
                print >>fp, name
            elif '\n' not in content:
                # one line with optional newline; distinguishable from
                # multiple lines by value starting on the same line,
                # even if it is wordwrapped for display

                # presence of final newline is not encoded in any way,
                # on purpose.
                print >>fp, '\n'.join(textwrap.wrap(
                        content,
                        initial_indent='%s=' % name,
                        subsequent_indent='\t',
                        break_long_words=False,
                        ))
            else:
                print >>fp, '%s=' % name
                print >>fp, '\n'.join([
                        '\t%s' % line
                        for line in content.split('\n')
                        ])
