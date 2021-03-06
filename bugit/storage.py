from __future__ import with_statement

import os
import subprocess

from bugit import util

def git_init(repo):
    returncode = subprocess.call(
        args=[
            'git',
            'init',
            '--quiet',
            ],
        cwd=repo,
        close_fds=True,
        )
    if returncode != 0:
        raise RuntimeError('git init failed')

def git_rev_parse(rev, repo=None):
    if repo is None:
        repo = '.'
    process = subprocess.Popen(
        args=[
            'git',
            'rev-parse',
            '--default',
            rev,
            ],
        cwd=repo,
        close_fds=True,
        stdout=subprocess.PIPE,
        )
    sha = process.stdout.read()
    returncode = process.wait()
    if returncode != 0:
        raise RuntimeError('git rev-parse failed')
    if not sha:
        return None
    sha = sha.rstrip('\n')
    return sha

def git_mktree(children, repo=None):
    if repo is None:
        repo = '.'
    process = subprocess.Popen(
        args=[
            'git',
            'mktree',
            '-z',
            ],
        cwd=repo,
        close_fds=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        )
    for (mode, type_, object, basename) in children:
        process.stdin.write(
            '%s %s %s\t%s\0' % (mode, type_, object, basename))
    process.stdin.close()

    tree = process.stdout.read()
    returncode = process.wait()
    if returncode != 0:
        raise RuntimeError('git mktree failed')
    tree = tree.splitlines()[0]
    return tree

def git_commit_tree(
    tree,
    message=None,
    repo=None,
    parents=None,
    ):
    if repo is None:
        repo = '.'
    args = [
        'git',
        'commit-tree',
        tree,
        ]
    if parents is not None:
        for parent in parents:
            args.extend(['-p', parent])
    process = subprocess.Popen(
        args=args,
        cwd=repo,
        close_fds=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        )
    if message is not None:
        process.stdin.write(message)
    process.stdin.close()
    commit = process.stdout.read()
    returncode = process.wait()
    if returncode != 0:
        raise RuntimeError('git commit-tree failed')
    commit = commit.splitlines()[0]
    return commit

def git_update_ref(
    ref,
    sha,
    old_sha=None,
    repo=None,
    ):

    args = [
        'git',
        'update-ref',
        ref,
        sha,
        ]
    if old_sha is not None:
        args.append(old_sha)
    returncode = subprocess.call(
        args=args,
        cwd=repo,
        close_fds=True,
        )
    if returncode != 0:
        raise RuntimeError('git update-ref failed')

def init(repo):
    """
    Initialize bug tracking component of existing repository.
    """
    util.mkdir(os.path.join(repo, '.git', 'bugit'))

    # does refs/heads/bugit/master exist?
    if git_rev_parse(
        rev='refs/heads/bugit/master',
        repo=repo,
        ) is None:
        # it did not, so create it

        # first create empty tree
        tree = git_mktree(
            children=[],
            repo=repo,
            )

        # create a commit that points to empty tree
        commit = git_commit_tree(
            tree=tree,
            message='Initial creation of bugit tree.',
            repo=repo,
            )

        # make a ref point to that tree
        git_update_ref(
            ref='refs/heads/bugit/master',
            sha=commit,
            old_sha=40*'0',
            repo=repo,
            )

    # does bugit/HEAD exist?
    process = subprocess.Popen(
        args=[
            'git',
            'symbolic-ref',
            '--quiet',
            'bugit/HEAD',
            ],
        cwd=repo,
        close_fds=True,
        stdout=subprocess.PIPE,
        )
    head = process.stdout.read()
    returncode = process.wait()
    if returncode not in [0, 1]:
        raise RuntimeError('git symbolic-ref failed')

    if not head:
        # it did not, so create it
        returncode = subprocess.call(
            args=[
                'git',
                'symbolic-ref',
                'bugit/HEAD',
                'refs/heads/bugit/master',
                ],
            cwd=repo,
            close_fds=True,
            )
        if returncode != 0:
            raise RuntimeError('git symbolic-ref failed')

def get(path, rev=None, repo=None):
    """Get value of variable, for pure read-only use."""
    if rev is None:
        rev = 'bugit/HEAD'
    if repo is None:
        repo = '.'
    for (mode, type_, object, basename) in git_ls_tree(
        path=path,
        treeish=rev,
        repo=repo,
        children=False,
        ):
        if type_ != 'blob':
            raise RuntimeError('cannot get non-blobs')
        process = subprocess.Popen(
            args=[
                'git',
                'cat-file',
                'blob',
                object,
                ],
            cwd=repo,
            close_fds=True,
            stdout=subprocess.PIPE,
            )
        data = process.stdout.read()
        returncode = process.wait()
        if returncode != 0:
            raise RuntimeError('git cat-file failed')
        return data


def git_ls_tree(
    path=None,
    treeish=None,
    repo=None,
    children=None,
    ):
    if path is None:
        path = ''
    if repo is None:
        repo = '.'
    if treeish is None:
        treeish = 'bugit/HEAD'
    if children is None:
        children = True
    assert not path.startswith('/')
    assert not path.endswith('/')
    if children:
        if path:
            path = path+'/'
    process = subprocess.Popen(
        args=[
            'git',
            'ls-tree',
            '-z',
            '--full-name',
            treeish,
            '--',
            path,
            ],
        cwd=repo,
        close_fds=True,
        stdout=subprocess.PIPE,
        )
    buf = ''
    while True:
        new = process.stdout.read(8192)
        buf += new
        while True:
            try:
                (entry, buf) = buf.split('\0', 1)
            except ValueError:
                break
            meta, filename = entry.split('\t', 1)
            mode, type_, object = meta.split(' ', 2)
            if children:
                assert filename.startswith(path)
                basename = filename[len(path):]
            else:
                assert filename == path
                basename = filename
            yield (mode, type_, object, basename)
        if not new:
            break
    if buf:
        raise RuntimeError(
            'git ls-tree output did not end in NUL')
    returncode = process.wait()
    if returncode != 0:
        raise RuntimeError('git ls-tree failed')

def ls(path, rev=None, repo=None):
    """Generate names of variables, for pure read-only use."""
    if rev is None:
        rev = 'bugit/HEAD'
    if repo is None:
        repo = '.'
    assert not path.endswith('/')
    path = path+'/'
    process = subprocess.Popen(
        args=[
            'git',
            'ls-tree',
            '-r',
            '--name-only',
            '--full-name',
            '-z',
            rev,
            path,
            ],
        cwd=repo,
        close_fds=True,
        stdout=subprocess.PIPE,
        )
    buf = ''
    while True:
        new = process.stdout.read(8192)
        buf += new
        while True:
            try:
                (entry, buf) = buf.split('\0', 1)
            except ValueError:
                break
            assert entry.startswith(path)
            yield entry[len(path):]
        if not new:
            break
    if buf:
        raise RuntimeError(
            'git ls-tree output did not end in NUL')
    returncode = process.wait()
    if returncode != 0:
        raise RuntimeError('git ls-tree failed')


class RaceCondition(Exception):
    """Update lost a race condition, retry"""
    pass

class Snapshot(object):
    """
    Consistent snapshot view to a git repository.
    """

    def __init__(self, **kw):
        repo = kw.pop('repo', None)
        if repo is None:
            repo = '.'
        self.repo = repo
        ref = kw.pop('ref', None)
        if ref is None:
            ref = 'bugit/HEAD'
        self.ref = ref
        super(Snapshot, self).__init__(**kw)

    def __enter__(self):
        head = git_rev_parse(
            rev=self.ref,
            repo=self.repo,
            )
        if head is None:
            raise RuntimeError('Repository is missing ref')
        self.head = head
        return self

    def __exit__(self, type_, value, traceback):
        pass

    def ls(self, path):
        return ls(
            repo=self.repo,
            rev=self.head,
            path=path,
            )

    def get(self, path):
        return get(
            path=path,
            repo=self.repo,
            rev=self.head,
            )


class Transaction(Snapshot):
    """
    Transacted write interface to git.

    Note that reads performed through this interface do not
    see the edits made within this transaction!
    """

    # Storing the ref value as of when we started actually has false
    # conflicts, so instead we could store the SHA1s of values
    # .get()'ed, and then, when committing, check:
    #
    # 1) ref has not changed -> easy
    #
    # 2) ref has changed -> check if .get()'ed
    #    values changed:
    #
    #    2a) no -> refresh is easy, loop to 1)
    #
    #    2b) yes -> raise RaceCondition
    #
    # Then again, it would probably be even nicer to just use git's
    # merging facilities for this. Would need to do a checkout
    # somewhere, as they need a working directory or at least index.
    # But still, code reuse sounds like a smart idea.

    def __init__(self, **kw):
        self.message = kw.pop('message', None)
        super(Transaction, self).__init__(**kw)

    def __enter__(self):
        r = super(Transaction, self).__enter__()
        self._edits = {}
        return r

    def _write_object(self, content):
        process = subprocess.Popen(
            args=[
                'git',
                'hash-object',
                '-w',
                '--stdin',
                ],
            cwd=self.repo,
            close_fds=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            )
        process.stdin.write(content)
        process.stdin.close()
        sha = process.stdout.read().rstrip('\n')
        returncode = process.wait()
        if returncode != 0:
            raise RuntimeError('git hash-object failed')
        if not sha:
            raise RuntimeError('git hash-object did not return a hash')
        return sha

    def _children_as_dict(self, path):
        r = {}
        for (mode, type_, object, basename) in git_ls_tree(
            path=path,
            repo=self.repo,
            ):
            r[basename] = (mode, type_, object)
        return r

    def _edit_tree(self, path, edits):
        children = self._children_as_dict(path)

        for k,v in edits.items():
            if isinstance(v, dict):
                child_sha = self._edit_tree(os.path.join(path, k), v)
                children[k] = ('040000', 'tree', child_sha)
            elif v is None:
                try:
                    del children[k]
                except KeyError:
                    pass
            else:
                child_sha = self._write_object(v)
                children[k] = ('100644', 'blob', child_sha)

        sha = git_mktree(
            children=(
                (mode, type_, object, name)
                for (name, (mode, type_, object)) in children.items()
                ),
            repo=self.repo,
            )
        return sha

    def __exit__(self, type_, value, traceback):
        super(Transaction, self).__exit__(type_, value, traceback)

        # store the tree in any case, for disaster recovery and
        # debugging
        tree = self._edit_tree(path='', edits=self._edits)
        commit = git_commit_tree(
            tree=tree,
            message=self.message,
            repo=self.repo,
            parents=[self.head],
            )

        if (type_ is None
            and value is None
            and traceback is None):
            # but only actually use the results if this is a success
            git_update_ref(
                ref=self.ref,
                sha=commit,
                old_sha=self.head,
                repo=self.repo,
                )
        else:
            return False

    def _record(self, path, content):
        cur = self._edits
        segments = path.split(os.sep)
        for segment in segments[:-1]:
            cur = cur.setdefault(segment, {})
        cur[segments[-1]] = content

    def set(self, path, content):
        self._record(path, content)

    def rm(self, path):
        self._record(path, None)
