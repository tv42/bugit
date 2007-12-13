from nose.tools import eq_ as eq

import errno
import os
import pkg_resources
import shutil
import sys

from cStringIO import StringIO

from bugit.util import mkdir

def find_test_name():
    try:
        from nose.case import Test
        from nose.suite import ContextSuite
        import types
        def get_nose_name(its_self):
            if isinstance(its_self, Test):
                file_, module, class_ = its_self.address()
                name = '%s:%s' % (module, class_)
                return name
            elif isinstance(its_self, ContextSuite):
                if isinstance(its_self.context, types.ModuleType):
                    return its_self.context.__name__
    except ImportError:
        # older nose
        from nose.case import FunctionTestCase, MethodTestCase
        from nose.suite import TestModule
        from nose.util import test_address
        def get_nose_name(its_self):
            if isinstance(its_self, (FunctionTestCase, MethodTestCase)):
                file_, module, class_ = test_address(its_self)
                name = '%s:%s' % (module, class_)
                return name
            elif isinstance(its_self, TestModule):
                return its_self.moduleName

    i = 0
    while True:
        i += 1
        frame = sys._getframe(i)
        # kludge, hunt callers upwards until we find our nose
        if (frame.f_code.co_varnames
            and frame.f_code.co_varnames[0] == 'self'):
            its_self = frame.f_locals['self']
            name = get_nose_name(its_self)
            if name is not None:
                return name

def maketemp():
    tmp = os.path.join(os.path.dirname(__file__), 'tmp')
    mkdir(tmp)

    name = find_test_name()
    tmp = os.path.join(tmp, name)
    try:
        shutil.rmtree(tmp)
    except OSError, e:
        if e.errno == errno.ENOENT:
            pass
        else:
            raise
    os.mkdir(tmp)
    return tmp

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
    allow_stderr=False,
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
    result.stderr = stderr.getvalue()
    if not allow_stderr:
        eq(result.stderr, '')
    eq(retcode, exit_status)
    return result
