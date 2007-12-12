#!/usr/bin/python
from setuptools import setup, find_packages
import os

setup(
    name = "bugit",
    version = "0.1",
    packages = find_packages(),

    author = "Tommi Virtanen",
    author_email = "tv@eagain.net",
    description = "distributed issue tracker using git for storage",
    long_description = """

Track bugs in a separate disconnected history in the same git
repository that houses your code.

""".strip(),
    license = "No public licensing; contact author",
    keywords = "issue-tracker distributed git",
    url = "http://eagain.net/software/bugit/",

    entry_points = {
        'console_scripts': [
            'bugit = bugit.cli:main',
            ],
        'bugit.command': [
            'list = bugit.cmd_list:main',
            'show = bugit.cmd_show:main',
            ],
        },

    test_suite = 'nose.collector'

    )

