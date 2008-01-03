from nose.tools import eq_ as eq

import errno
import os
import pkg_resources
import shutil
import subprocess
import sys

from cStringIO import StringIO

from bugit import storage
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
    def check_stdout(self, want):
        eq(
            self.stdout,
            want,
            'stdout does not match:\n%s' % self.stdout,
            )

    def check_stderr(self, want):
        eq(
            self.stderr,
            want,
            'stderr does not match:\n%s' % self.stderr,
            )

def _get_script():
    my_distr = list(
        pkg_resources.find_distributions('.', only=True)
        )[0]

    return my_distr.load_entry_point('console_scripts', 'bugit')

def clitest(
    args,
    stdin=None,
    exit_status=None,
    allow_stderr=False,
    cwd=None,
    ):
    if stdin is None:
        stdin = ''
    if exit_status is None:
        exit_status = 0

    args = ['bugit']+args
    script = _get_script()

    stdin = StringIO(stdin)
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
        olddir = os.open('.', os.O_RDONLY|os.O_DIRECTORY)
        if cwd is not None:
            os.chdir(cwd)
        try:
            try:
                retcode = script()
            except SystemExit, e:
                retcode = e.code
            else:
                if retcode is None:
                    retcode = 0
        finally:
            os.fchdir(olddir)
            os.close(olddir)
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

def check_bugit_repository(repo):
    assert os.path.isdir(os.path.join(repo, '.git', 'bugit'))
    eq(os.listdir(os.path.join(repo, '.git', 'bugit')), [])

    sha = storage.git_rev_parse(
        rev='refs/bugit/master',
        repo=repo,
        )
    assert sha is not None

    process = subprocess.Popen(
        args=[
            'git',
            'symbolic-ref',
            'refs/bugit/HEAD',
            ],
        cwd=repo,
        close_fds=True,
        stdout=subprocess.PIPE,
        )
    got = process.stdout.read()
    returncode = process.wait()
    eq(returncode, 0)
    eq(got, 'refs/bugit/master\n')

def assert_raises(excClass, callableObj, *args, **kwargs):
    """
    Like unittest.TestCase.assertRaises, but returns the exception.
    """
    try:
        callableObj(*args, **kwargs)
    except excClass, e:
        return e
    else:
        if hasattr(excClass,'__name__'): excName = excClass.__name__
        else: excName = str(excClass)
        raise AssertionError("%s not raised" % excName)
