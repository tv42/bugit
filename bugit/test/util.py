from nose.tools import eq_ as eq

import pkg_resources
import sys
from cStringIO import StringIO

class CLITestResult(object):
    pass

def _get_script():
    my_distr = list(
        pkg_resources.find_distributions('.', only=True)
        )[0]

    return my_distr.load_entry_point('console_scripts', 'bugit')

def clitest(
    args,
    exit_status=None,
    ):
    if exit_status is None:
        exit_status = 0

    args = ['bugit']+args
    script = _get_script()

    stdin = StringIO('')
    stdout = StringIO()
    stderr = StringIO()
    (old_stdin, sys.stdin,
     old_stdout, sys.stdout,
     old_stderr, sys.stderr,
     old_argv, sys.argv,
     ) = (
        sys.stdin, stdin,
        sys.stdout, stdout,
        sys.stderr, stderr,
        sys.argv, args,
        )
    try:
        try:
            retcode = script()
        except SystemExit, e:
            retcode = e.code
        else:
            if retcode is None:
                retcode = 0
    finally:
        (sys.stdin,
         sys.stdout,
         sys.stderr,
         sys.argv,
         ) = (
            old_stdin,
            old_stdout,
            old_stderr,
            old_argv,
            )

    result = CLITestResult()
    result.stdout = stdout.getvalue()
    eq(stderr.getvalue(), '')
    eq(retcode, exit_status)
    return result
