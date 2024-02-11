# PyQt-builder - the PyQt Build System

PyQt-builder is the PEP 517 compliant build system for PyQt and projects that
extend PyQt.  It extends the [SIP](https://pypi.org/project/sip/) build system
and uses Qt's `qmake` to perform the actual compilation and installation of
extension modules.

Projects that use PyQt-builder provide an appropriate `pyproject.toml` file and
an optional `project.py` script.  Any PEP 517 compliant frontend, for example
`build` or `pip` can then be used to build and install the project.


## Documentation

The documentation can be found at
[Read the Docs](https://PyQt-builder.readthedocs.io).


## License

PyQt-builder is licensed under the BSD 2 clause license.


## Installation

To install SIP, run:

    pip install sip


## Creating Packages for Distribution

Python sdists and wheels can be created with any standard Python build
frontend.

For example, using [build](https://pypi.org/project/build/) an sdist and wheel
will be created from a checkout in the current directory by running:

    python -m build --outdir .


## Building the Documentation

The documentation is built using [Sphinx](https://pypi.org/project/Sphinx/),
[myst_parser](https://pypi.org/project/myst-parser/) and the
[sphinx-rtd-theme](https://pypi.org/project/sphinx-rtd-theme/) theme.

Change to the `docs` directory of a checkout and run:

    make html

The HTML documentation can then be found in the `_build/html` subdirectory.
