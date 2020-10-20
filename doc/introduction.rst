Introduction
============

PyQt-builder is a tool for generating `Python <https://www.python.org>`__
bindings for C++ libraries that use the `Qt <https://www.qt.io>`__ application
framework.  The bindings are built on top of the `PyQt
<https://www.riverbankcomputing.com/software/pyqt/>`__ bindings for Qt.
PyQt-builder is used to build PyQt itself.

PyQt-builder also includes the :program:`pyqt-bundle` command line tool used to
bundle a copy of Qt with a PyQt wheel.  This is separate from the build system
and described in :ref:`ref-pyqt-bundle`.

PyQt-builder is actually an extension of the `PEP 384
<https://www.python.org/dev/peps/pep-0517/>`__-compliant
`SIP <https://www.riverbankcomputing.com/software/sip/>`__ bindings generator
and build system.  In the simplest cases all that is needed is a
:file:`pyproject.toml` file that specifies how the bindings are to be
generated.  More complicated cases require additional code, typically
implemented in a :file:`project.py` file.

SIP provides a number of task-orientated command line tools and a
:py:mod:`sipbuild` module which can be used to extend the build system.  The
command line tools include :program:`sip-install` to build and install a set of
bindings, and :program:`sip-wheel` to create a wheel that can be uploaded to
`PyPI <https://pypi.org>`__.

PyQt-builder doesn't provide any additional command line build tools but does
extend the SIP tools by providing additional command line options and options
that can be specified in the :file:`pyproject.toml` file.  These are
implemented by the :py:mod:`pyqtbuild` module which also provides an API that
can be used by a project's :file:`project.py` file.

This documentation assumes you are already familiar with the `SIP documentation
<https://www.riverbankcomputing.com/static/Docs/sip/>`__.


Installation
------------

To install PyQt-builder from PyPI, run::

    pip install PyQt-builder
