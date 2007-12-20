import os

def _strip_prefix(l):
    """
    Go through the lines and strip common leading prefix.

    For now, only supports tab.
    """
    shortest_prefix = None
    for line in l:
        if not line.strip():
            continue
        nonws = line.lstrip(' \t')
        prefix = line[:-len(nonws)]
        length = 0
        for char in prefix:
            if char == ' ':
                length += 1
            elif char == '\t':
                # tab means round up to next 8
                length = (int(length/8)+1)*8
            else:
                raise RuntimeError()
        if shortest_prefix is None:
            shortest_prefix = length
        else:
            shortest_prefix = min(length, shortest_prefix)

    assert shortest_prefix > 0
    for line in l:
        if not line.strip():
            yield ''
        else:
            to_strip = shortest_prefix
            while to_strip:
                assert line
                if line[0] == '\t':
                    line = 8*' ' + line[1:]

                assert line[0] == ' '
                line = line[1:]
                to_strip -= 1
            yield line

def _process(value):
    if len(value) == 1:
        # single line not wordwrapped
        return value[0] + '\n'
    elif not value[0]:
        # multi-line
        # ignore the first (empty) line
        value = list(_strip_prefix(value[1:]))
        separator = '\n'
    else:
        # single line
        # first line is not indented
        value = [value[0]] + list(_strip_prefix(value[1:]))
        separator = ' '

    return separator.join(value) + '\n'

class _State(object):
    def __init__(self, name):
        self.__doc__ = name
    def __str__(self):
        return self.__doc__

MAYBE_HEADER = _State('MAYBE_HEADER')
HEADER = _State('HEADER')
DESCRIPTION = _State('DESCRIPTION')
VARIABLES = _State('VARIABLES')

def parse_ticket_raw(fp):
    state = MAYBE_HEADER
    variable = None
    value = []
    for line in fp:
        line = line.rstrip()

        if state is MAYBE_HEADER:
            first_space = line.find(' ')
            first_equals = line.find('=')
            if (first_space != -1
                and (first_equals == -1
                     or first_space < first_equals)):
                state = HEADER
            else:
                state = VARIABLES

        if (state is HEADER
            and not line):
            if variable is not None:
                yield (variable, _process(value))
                variable = None
                value = []
            state = DESCRIPTION
            variable = '_description'
            value.append('')
        elif not line or line.startswith(('\t', ' ')):
            assert variable is not None
            value.append(line)
        else:
            if variable is not None:
                if state is DESCRIPTION:
                    while not value[-1]:
                        del value[-1]
                yield (variable, _process(value))
                variable = None
                value = []

            if '=' not in line:
                if ' ' not in line:
                    # empty value, cannot ever be multiline!
                    yield (line, '')
                else:
                    k,v = line.split(' ', 1)
                    variable = '_%s' % k
                    value.append(v)
            else:
                k,v = line.split('=', 1)
                variable = k
                value.append(v)

    yield (variable, _process(value))

def parse_ticket(fp):
    for (variable, value) in parse_ticket_raw(fp):
        if variable.startswith('_'):
            if variable == '_ticket':
                yield (variable, value)
            elif variable == '_number':
                yield ('number', value)
            elif variable == '_description':
                yield ('description', value)
            elif variable == '_tags':
                tags = value.split(None)
                for tag in tags:
                    yield (os.path.join('tags', tag), '')
            elif variable == '_seen':
                # TODO
                pass
            else:
                raise RuntimeError('Unknown special variable: %r' % variable)
        else:
            yield (variable, value)
