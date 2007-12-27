import os
import re

class InvalidHeaderError(Exception):
    """Invalid header"""

    def __str__(self):
        return ': '.join([self.__doc__]+list(self.args))

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
        v = value[0]
        if v:
            v = v + '\n'
        return v
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

_HEADER_RE = re.compile(r'^(?P<command>[a-z_][a-z0-9_./@:-]*)(?:\s+(?P<value>.*))?$')
_VARIABLE_RE = re.compile(r'^(?P<variable>[a-z_][a-z0-9_./@:-]*)(?:=(?P<value>.*))?$')

def _parse_header(lines):
    seen_header = False
    command = None
    value = []
    for line in lines:
        line = line.rstrip()
        if line.startswith(('\t', ' ')):
            if command is None:
                raise InvalidHeaderError(
                    'Cannot start with a continuation line',
                    repr(line),
                    )
            value.append(line)
            continue
        if command is not None:
            yield ('_%s' % command, _process(value))
            seen_header = True
            command = None
            value = []
        if not line:
            break
        match = _HEADER_RE.match(line)
        if match is None:
            raise InvalidHeaderError(
                "Line does not look like a header",
                repr(line),
                )
        command = match.group('command')
        value = [match.group('value')]

    if command is not None:
        yield ('_%s' % command, _process(value))
        seen_header = True

    if not seen_header:
        raise InvalidHeaderError(
            "Header had no complete lines",
            )

def parse_ticket_raw(lines, strict=False):
    for r in _parse_header(lines):
        yield r

    description_lines = []

    for line in lines:
        if line.rstrip() == '--':
            break

        description_lines.append(line)

    while description_lines and description_lines[-1] == '\n':
        del description_lines[-1]
    description = ''.join(description_lines)
    if description:
        yield ('_description', description)

    variable = None
    value = []
    for line in lines:
        line = line.rstrip()

        if not line or line.startswith(('\t', ' ')):
            if variable is not None:
                value.append(line)
            else:
                # before the first variable, only empty lines are
                # allowed
                assert not line
        else:
            if variable is not None:
                yield (variable, _process(value))
                variable = None
                value = []

            match = _VARIABLE_RE.match(line)
            assert match is not None
            variable = match.group('variable')
            v = match.group('value')
            if v is None:
                v = ''
            value.append(v)

    if variable is not None:
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
            elif variable == '_nop':
                pass
            else:
                raise RuntimeError('Unknown special variable: %r' % variable)
        else:
            yield (variable, value)
