import errno
import os

def mkdir(*a, **kw):
    try:
        os.mkdir(*a, **kw)
    except OSError, e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

def extract_title(description):
    l = []
    while True:
        try:
            (line, description) = description.split('\n', 1)
        except ValueError:
            break

        if not line.strip():
            # empty (or whitespace-only) line separates title from
            # description
            break

        l.append(line)

    return ('\n'.join(l), description)
