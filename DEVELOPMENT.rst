=========================
 Development information
=========================

Due to reasons to do with setuptools complexity, you need to run this
before working with the package::

	setup.py egg_dist

And then, when running unit tests, always include current directory in
``PYTHONPATH``::

	PYTHONPATH=. nosetests

If you want to have the shell-runnable commands available directly
in your development environment, you need to run::

	install -d stage/lib stage/bin
	export PYTHONPATH="$PWD/stage/lib"
	./setup.py develop --install-dir=stage/lib --script-dir=stage/bin

And then you can run::

	PYTHONPATH=. ./stage/bin/bugit --help
